from __future__ import annotations

import logging
from datetime import date
from pathlib import Path

import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession

from src.config.settings import settings
from src.features.forecasting.ml.model_factory import create_regressor
from src.features.forecasting.ml.shap_explainer import tree_shap_contributions
from src.features.forecasting.models.forecast import Forecast
from src.features.forecasting.models.model_metadata import ModelMetadata
from src.features.forecasting.pipeline.data_cleaning import SalesDataCleaningService
from src.features.forecasting.pipeline.metrics import mae, mape, rmse
from src.features.forecasting.pipeline.order_optimization import suggested_order_quantity
from src.features.forecasting.repositories.forecast_repository import ForecastRepository
from src.features.forecasting.repositories.model_metadata_repository import (
    ModelMetadataRepository,
)
from src.features.forecasting.services.feature_engineering_service import (
    FeatureEngineeringService,
)
from src.features.forecasting.services.model_manager import ModelManager
from src.features.forecasting.schemas.forecast_schema import (
    ForecastPoint,
    ForecastRequest,
    ForecastResponse,
    ShapFactorContribution,
    TrainFromDbResponse,
)
from src.features.sales.repositories.sale_repository import SalesRepository


logger = logging.getLogger(__name__)

MIN_HISTORY_ROWS = 45


def _sales_to_dataframe(sales: list) -> pd.DataFrame:
    rows: list[dict] = []
    for s in sales:
        promo = 0.0
        if s.import_extras and isinstance(s.import_extras, dict):
            raw = s.import_extras.get("promo")
            if raw is not None:
                try:
                    promo = float(raw)
                except (TypeError, ValueError):
                    promo = 0.0
        rows.append(
            {
                "sale_date": pd.Timestamp(s.sale_date),
                "quantity": float(s.quantity),
                "price": float(s.price) if s.price is not None else 0.0,
                "promo": promo,
                "shop_id": int(s.warehouse_id) if s.warehouse_id is not None else 0,
                "item_id": int(s.product_id) if s.product_id is not None else 0,
                "item_category_id": int(
                    (s.import_extras or {}).get("item_category_id")
                    or (s.import_extras or {}).get("category_id")
                    or (s.import_extras or {}).get("category_key")
                    or 0
                ),
            }
        )
    return pd.DataFrame(rows)


class ForecastingService:
    """Пайплайн: очистка → признаки → LightGBM/CatBoost → прогноз → заказ."""

    def __init__(self) -> None:
        self.feature_service = FeatureEngineeringService()
        self.cleaner = SalesDataCleaningService()
        self.model_manager = ModelManager()
        self._estimator = None
        self._feature_columns: list[str] | None = None
        self._backend: str | None = None

    def _load_payload(self) -> dict:
        if not self.model_manager.exists():
            raise FileNotFoundError("Модель не обучена: вызовите POST /forecast/train")
        payload = self.model_manager.load()
        self._estimator = payload["estimator"]
        self._feature_columns = payload.get("feature_columns")
        self._backend = payload.get("backend")
        return payload

    def _ensure_model(self) -> None:
        if self._estimator is None:
            self._load_payload()

    def train_from_dataframe(
        self,
        df: pd.DataFrame,
        *,
        product_key: str = "global",
        backend: str | None = None,
    ) -> dict:
        if len(df) < MIN_HISTORY_ROWS:
            raise ValueError(
                f"Недостаточно истории: нужно ≥{MIN_HISTORY_ROWS} строк, есть {len(df)}"
            )

        cleaned = self.cleaner.clean(df)
        feat = self.feature_service.create_features(cleaned)
        if feat.empty or len(feat) < 20:
            raise ValueError("После признаков не осталось достаточного числа строк")

        drop_cols = {"sale_date", "target_quantity"}
        feature_cols = [c for c in feat.columns if c not in drop_cols]
        X = feat[feature_cols]
        y = feat["target_quantity"]

        split = max(int(len(feat) * 0.8), 28)
        if split >= len(feat):
            split = len(feat) - 1
        if split < 1:
            raise ValueError("Недостаточно данных для time-series split")
        X_train, X_test = X.iloc[:split], X.iloc[split:]
        y_train, y_test = y.iloc[:split], y.iloc[split:]

        selected_backend = backend or settings.FORECAST_MODEL_BACKEND
        logger.info(
            "Training forecast model",
            extra={
                "backend": selected_backend,
                "rows": len(feat),
                "feature_count": len(feature_cols),
                "split_index": split,
            },
        )
        estimator = create_regressor(selected_backend)
        estimator.fit(X_train, y_train)
        y_pred = estimator.predict(X_test)
        mape_v = mape(y_test.values, y_pred)
        rmse_v = rmse(y_test.values, y_pred)
        mae_v = mae(y_test.values, y_pred)

        estimator.fit(X, y)

        trained_at = date.today().isoformat()
        payload = {
            "estimator": estimator,
            "feature_columns": feature_cols,
            "backend": selected_backend,
            "mape": float(mape_v),
            "rmse": float(rmse_v),
            "mae": float(mae_v),
            "product_key": product_key,
            "trained_at": trained_at,
        }
        path = self.model_manager.save(payload)
        version = self.model_manager.get_latest_version()
        self.model_manager.append_training_event(
            {
                "trained_at": trained_at,
                "version": version,
                "product_key": product_key,
                "backend": selected_backend,
                "rows": len(feat),
                "mape": float(mape_v),
                "rmse": float(rmse_v),
                "mae": float(mae_v),
            }
        )
        self._estimator = estimator
        self._feature_columns = feature_cols
        self._backend = selected_backend

        return {
            "model_path": str(path),
            "mape": float(mape_v),
            "rmse": payload["rmse"],
            "mae": payload["mae"],
            "backend": selected_backend,
            "rows": len(feat),
            "version": version,
            "trained_at": trained_at,
        }

    async def train_from_db(
        self,
        db: AsyncSession,
        product_id: int | None,
        warehouse_id: int | None,
        *,
        source: str = "db",
        csv_path: str | None = None,
        backend: str | None = None,
    ) -> TrainFromDbResponse:
        sales_repo = SalesRepository(db)
        if source == "csv":
            if not csv_path:
                raise ValueError("Для source=csv нужно передать csv_path")
            csv_file = Path(csv_path)
            if not csv_file.exists():
                raise ValueError(f"CSV файл не найден: {csv_path}")
            df = pd.read_csv(csv_file)
            rename_map = {
                "date": "sale_date",
                "sales": "quantity",
                "category_id": "item_category_id",
            }
            df = df.rename(columns=rename_map)
            required = {"sale_date", "quantity"}
            if not required.issubset(set(df.columns)):
                raise ValueError("CSV должен содержать как минимум столбцы sale_date и quantity")
            if "price" not in df.columns:
                df["price"] = 0.0
            if "shop_id" not in df.columns:
                df["shop_id"] = 0
            if "item_id" not in df.columns:
                df["item_id"] = product_id or 0
            if "item_category_id" not in df.columns:
                df["item_category_id"] = 0
        else:
            if product_id is None:
                sales = await sales_repo.get_all()
            else:
                sales = await sales_repo.get_by_product_and_warehouse(product_id, warehouse_id)
            df = _sales_to_dataframe(sales)
        if df.empty:
            raise ValueError("Нет данных для обучения")

        stats = self.train_from_dataframe(
            df,
            product_key=f"{product_id or 'all'}_{warehouse_id or 'all'}",
            backend=backend,
        )

        meta_repo = ModelMetadataRepository(db)
        await meta_repo.add(
            ModelMetadata(
                name=f"product_{product_id or 'all'}",
                version=f"v{stats['version']}",
                algorithm=stats["backend"],
                mape=stats.get("mape"),
                rmse=stats.get("rmse"),
                model_path=stats["model_path"],
            )
        )

        return TrainFromDbResponse(
            product_id=product_id,
            warehouse_id=warehouse_id,
            rows_used=stats["rows"],
            mape=stats.get("mape"),
            rmse=stats.get("rmse"),
            mae=stats.get("mae"),
            backend=stats["backend"],
            model_path=stats["model_path"],
            model_version=stats["version"],
            trained_at=date.fromisoformat(stats["trained_at"]),
        )

    def _recursive_forecast(
        self,
        df_cleaned: pd.DataFrame,
        horizon_days: int,
    ) -> list[float]:
        self._ensure_model()
        assert self._estimator is not None
        assert self._feature_columns is not None

        hist = df_cleaned.copy()
        preds: list[float] = []

        for _ in range(horizon_days):
            feat = self.feature_service.create_features(hist.copy())
            if feat.empty:
                break
            last = feat.iloc[-1:]
            X = last[self._feature_columns]
            pred = float(self._estimator.predict(X)[0])
            preds.append(pred)

            next_date = pd.Timestamp(hist["sale_date"].iloc[-1]) + pd.Timedelta(days=1)
            hist = pd.concat(
                [
                    hist,
                    pd.DataFrame(
                        {
                            "sale_date": [next_date],
                            "quantity": [pred],
                            "price": [hist["price"].iloc[-1]],
                            "promo": [0.0],
                            "shop_id": [hist["shop_id"].iloc[-1] if "shop_id" in hist.columns else 0],
                            "item_id": [hist["item_id"].iloc[-1] if "item_id" in hist.columns else 0],
                            "item_category_id": [
                                hist["item_category_id"].iloc[-1]
                                if "item_category_id" in hist.columns
                                else 0
                            ],
                        }
                    ),
                ],
                ignore_index=True,
            )

        return preds

    def _build_shap_explanation(
        self,
        df_cleaned: pd.DataFrame,
    ) -> tuple[list[ShapFactorContribution] | None, float | None]:
        """SHAP для строки признаков, соответствующей последнему месяцу истории (первый шаг прогноза)."""
        self._ensure_model()
        assert self._estimator is not None
        assert self._feature_columns is not None
        feat = self.feature_service.create_features(df_cleaned.copy())
        if feat.empty:
            return None, None
        last = feat.iloc[-1:]
        X = last[self._feature_columns]
        try:
            raw_list, base = tree_shap_contributions(self._estimator, X)
            conv = [
                ShapFactorContribution(
                    feature_name=x["feature_name"],
                    feature_value=x["feature_value"],
                    shap_value=x["shap_value"],
                )
                for x in raw_list
            ]
            return (conv if conv else None), base
        except Exception:
            logger.warning("SHAP explanation failed", exc_info=True)
            return None, None

    async def generate_forecast(
        self,
        db: AsyncSession,
        data: ForecastRequest,
    ) -> ForecastResponse:
        self._load_payload()

        pid = int(str(data.product_id).strip())
        wid = int(data.warehouse_id) if data.warehouse_id not in (None, "") else None

        sales_repo = SalesRepository(db)
        sales = await sales_repo.get_by_product_and_warehouse(pid, wid)
        df = _sales_to_dataframe(sales)
        if len(df) < MIN_HISTORY_ROWS:
            raise ValueError(
                f"Недостаточно истории для прогноза (≥{MIN_HISTORY_ROWS} строк)"
            )

        cleaned = self.cleaner.clean(df)
        horizon_days = max(1, int(data.horizon_days))
        shap_explanation, shap_base = self._build_shap_explanation(cleaned)
        preds = self._recursive_forecast(cleaned, horizon_days)

        first_date = (pd.Timestamp(cleaned["sale_date"].iloc[-1]) + pd.Timedelta(days=1)).date()

        points: list[ForecastPoint] = []
        for i, p in enumerate(preds):
            points.append(
                ForecastPoint(
                    date=(pd.Timestamp(first_date) + pd.Timedelta(days=i)).date(),
                    predicted_sales=p,
                )
            )

        predicted_monthly_sales = preds[0] if preds else 0.0
        suggested: float | None = None
        if data.current_stock is not None:
            suggested = suggested_order_quantity(
                predicted_monthly_sales,
                data.current_stock,
                data.safety_stock,
                lead_time_months=data.lead_time_months,
            )

        forecast_repo = ForecastRepository(db)
        wid_store = wid if wid is not None else (sales[0].warehouse_id if sales else None)
        if wid_store is not None:
            meta_repo = ModelMetadataRepository(db)
            latest = await meta_repo.get_latest()
            model_id = latest.id if latest else None
            forecast_date = date.today()
            if model_id is not None:
                to_save = [
                    Forecast(
                        shop_id=None,
                        item_id=None,
                        product_id=pid,
                        warehouse_id=wid_store,
                        forecast_date=forecast_date,
                        target_date=pt.date,
                        predicted_quantity=pt.predicted_sales,
                        lower_bound=None,
                        upper_bound=None,
                        model_id=model_id,
                    )
                    for pt in points
                ]
                await forecast_repo.add_all(to_save)

        return ForecastResponse(
            product_id=str(pid),
            horizon=horizon_days,
            forecast=points,
            suggested_order_quantity=suggested,
            model_backend=self._backend,
            shap_explanation=shap_explanation,
            shap_base_value=shap_base,
        )

    async def retrain(
        self,
        db: AsyncSession,
        *,
        product_id: int | None,
        warehouse_id: int | None,
        source: str = "db",
        csv_path: str | None = None,
        backend: str | None = None,
    ) -> TrainFromDbResponse:
        return await self.train_from_db(
            db,
            product_id=product_id,
            warehouse_id=warehouse_id,
            source=source,
            csv_path=csv_path,
            backend=backend,
        )

    async def get_forecast_history(
        self,
        db: AsyncSession,
    ) -> list[ForecastResponse]:
        repo = ForecastRepository(db)
        rows = await repo.get_all()
        if not rows:
            return []

        by_product: dict[int, list] = {}
        for f in rows:
            by_product.setdefault(f.product_id, []).append(f)

        out: list[ForecastResponse] = []
        for pid, fs in by_product.items():
            fs_sorted = sorted(fs, key=lambda x: x.target_date or date.min)
            points = [
                ForecastPoint(
                    date=x.target_date,
                    predicted_sales=float(x.predicted_quantity),
                )
                for x in fs_sorted
                if x.target_date is not None
            ]
            horizon = len(points)
            out.append(
                ForecastResponse(
                    product_id=str(pid),
                    horizon=horizon,
                    forecast=points,
                    suggested_order_quantity=None,
                    model_backend=None,
                )
            )
        return out
