from datetime import date

from pydantic import BaseModel, Field


class ForecastRequest(BaseModel):
    product_id: str
    horizon_days: int = 7
    warehouse_id: str | None = None
    current_stock: float | None = Field(
        None,
        description="Остаток для расчёта рекомендуемого заказа (опционально)",
    )
    safety_stock: float = 0.0


class ForecastPoint(BaseModel):
    date: date
    predicted_sales: float


class ForecastResponse(BaseModel):
    product_id: str
    horizon: int
    forecast: list[ForecastPoint]
    suggested_order_quantity: float | None = None
    model_backend: str | None = None


class TrainFromDbRequest(BaseModel):
    product_id: int
    warehouse_id: int | None = None


class TrainFromDbResponse(BaseModel):
    product_id: int
    warehouse_id: int | None = None
    rows_used: int
    mape: float | None = None
    rmse: float | None = None
    backend: str
    model_path: str
