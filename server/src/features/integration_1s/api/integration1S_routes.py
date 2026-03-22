from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query, status
from fastapi.responses import Response
from pydantic import BaseModel
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.config.settings import settings

from ..dependencies import get_api_key
from ..models.apikey_model import ApiKey
from ..client.odata_client import ODataClient
from ..services.sync_service import SyncService
from ..services.kaggle_export_service import (
    build_kaggle_dataframes,
    kaggle_dataset_zip_bytes,
)
from ..services.onec_kaggle_fetch_service import fetch_kaggle_source_rows
from ..services.onec_sales_import_service import import_onec_sales_from_odata
from ..services.onec_push_service import OneCPushService


class PushOrdersBody(BaseModel):
    orders: list[dict]


class Integration1SRoutes:
    def __init__(self):
        self.router = APIRouter(
            prefix="/integration/1c",
            tags=["1C integration"],
        )
        self._register_routes()

    def _register_routes(self):
        @self.router.post("/sync-sales")
        async def sync_sales(
            api_key: ApiKey = Depends(get_api_key),
        ):
            # Инициализируем клиента и сервис синхронизации.
            client = ODataClient(
                base_url=settings.INTEGRATION_1C_BASE_URL,
                username=settings.INTEGRATION_1C_USERNAME,
                password=settings.INTEGRATION_1C_PASSWORD or "",
            )
            service = SyncService(client)

            sales_data = await service.sync_sales()

            return {
                "status": "sync completed",
                "synced_count": len(sales_data),
            }

        @self.router.get("/export/kaggle-dataset")
        async def export_kaggle_dataset(
            api_key: ApiKey = Depends(get_api_key),
        ):
            """
            Выгрузка ZIP с CSV в формате Kaggle «Predict Future Sales»:
            sales_train.csv, shops.csv, items.csv, item_categories.csv.
            Данные читаются из OData 1С (документ реализации + табличная часть).
            """
            if not settings.INTEGRATION_1C_BASE_URL or not settings.INTEGRATION_1C_USERNAME:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Интеграция с 1С не настроена: задайте INTEGRATION_1C_BASE_URL и INTEGRATION_1C_USERNAME в окружении",
                )
            client = ODataClient(
                base_url=settings.INTEGRATION_1C_BASE_URL,
                username=settings.INTEGRATION_1C_USERNAME,
                password=settings.INTEGRATION_1C_PASSWORD or "",
            )
            rows = await fetch_kaggle_source_rows(client, settings)
            dfs = build_kaggle_dataframes(rows)
            payload = kaggle_dataset_zip_bytes(dfs)
            return Response(
                content=payload,
                media_type="application/zip",
                headers={
                    "Content-Disposition": 'attachment; filename="kaggle_predict_future_sales.zip"'
                },
            )

        @self.router.post("/sync-sales-history")
        async def sync_sales_history(
            api_key: ApiKey = Depends(get_api_key),
            db: AsyncSession = Depends(get_db),
            lookback_days: int | None = Query(
                None,
                ge=0,
                description="Сдвиг «сегодня − N дней» для нижней границы (если не задано — из настроек или max(sale_date))",
            ),
            date_from: date | None = Query(
                None,
                description="Явная дата «с» для фильтра OData (приоритет над lookback_days)",
            ),
        ):
            """
            Дополнение истории продаж из 1С в БД. Обычно после первичной загрузки CSV (Kaggle).
            Граница даты: INTEGRATION_1C_SYNC_FROM_MAX_SALE_DATE + overlap, иначе lookback.
            """
            if not settings.INTEGRATION_1C_BASE_URL or not settings.INTEGRATION_1C_USERNAME:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Интеграция с 1С не настроена",
                )
            return await import_onec_sales_from_odata(
                db,
                settings,
                date_from=date_from,
                lookback_days_override=lookback_days,
            )

        @self.router.post("/push/orders")
        async def push_orders_to_1c(
            body: PushOrdersBody,
            api_key: ApiKey = Depends(get_api_key),
        ):
            """Рекомендуемые заказы / движения обратно в 1С (см. INTEGRATION_1C_PUSH_ORDERS_URL)."""
            svc = OneCPushService(settings)
            try:
                return await svc.push_orders(body.orders)
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_502_BAD_GATEWAY,
                    detail=str(e),
                ) from e
