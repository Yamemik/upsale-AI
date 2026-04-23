from datetime import date

from pydantic import BaseModel, Field
from typing import Literal


class ForecastRequest(BaseModel):
    product_id: str
    horizon_days: int = 7
    warehouse_id: str | None = None
    lead_time_months: float = Field(
        1.0,
        ge=0.0,
        description="Срок поставки в месяцах для расчёта заказа",
    )
    current_stock: float | None = Field(
        None,
        description="Остаток для расчёта рекомендуемого заказа (опционально)",
    )
    safety_stock: float = 0.0


class ForecastPoint(BaseModel):
    date: date
    predicted_sales: float


class ShapFactorContribution(BaseModel):
    feature_name: str
    feature_value: float | None = None
    shap_value: float


class ForecastResponse(BaseModel):
    product_id: str
    horizon: int
    forecast: list[ForecastPoint]
    suggested_order_quantity: float | None = None
    model_backend: str | None = None
    shap_explanation: list[ShapFactorContribution] | None = Field(
        default=None,
        description="Вклад признаков (SHAP) для первого шага прогноза",
    )
    shap_base_value: float | None = Field(
        default=None,
        description="Базовое ожидание модели (expected value)",
    )


class TrainFromDbRequest(BaseModel):
    product_id: int | None = None
    warehouse_id: int | None = None
    source: Literal["db", "csv"] = "db"
    csv_path: str | None = None
    model_backend: str | None = Field(
        default=None,
        description="lightgbm | catboost, если не задано — берется из settings",
    )


class TrainFromDbResponse(BaseModel):
    product_id: int | None = None
    warehouse_id: int | None = None
    rows_used: int
    mape: float | None = None
    rmse: float | None = None
    mae: float | None = None
    backend: str
    model_path: str
    model_version: int
    trained_at: date


class RetrainRequest(TrainFromDbRequest):
    pass
