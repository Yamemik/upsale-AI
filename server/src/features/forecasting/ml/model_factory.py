"""Фабрика регрессоров: LightGBM (по умолчанию) или CatBoost."""

from __future__ import annotations

from typing import Any


def create_regressor(backend: str) -> Any:
    b = (backend or "lightgbm").lower().strip()
    if b == "catboost":
        try:
            from catboost import CatBoostRegressor

            return CatBoostRegressor(
                depth=8,
                iterations=300,
                learning_rate=0.05,
                loss_function="RMSE",
                verbose=False,
            )
        except ImportError as e:
            raise ImportError(
                "Для backend=catboost установите пакет catboost: pip install catboost"
            ) from e

    import lightgbm as lgb

    return lgb.LGBMRegressor(
        n_estimators=300,
        learning_rate=0.05,
        max_depth=8,
    )
