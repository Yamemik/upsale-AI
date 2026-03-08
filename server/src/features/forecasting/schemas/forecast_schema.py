from datetime import date
from pydantic import BaseModel


class ForecastRequest(BaseModel):
    product_id: str
    horizon_days: int = 7


class ForecastPoint(BaseModel):
    date: date
    predicted_sales: float


class ForecastResponse(BaseModel):
    product_id: str
    horizon: int
    forecast: list[ForecastPoint]
