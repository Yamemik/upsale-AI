from datetime import datetime

from pydantic import BaseModel


class ReorderRecommendationBase(BaseModel):
    product_id: int
    warehouse_id: int
    recommended_quantity: float
    reorder_point: float
    lead_time_days: int


class ReorderRecommendationCreate(ReorderRecommendationBase):
    pass


class ReorderRecommendationUpdate(BaseModel):
    recommended_quantity: float | None = None
    reorder_point: float | None = None
    lead_time_days: int | None = None


class ReorderRecommendationOut(ReorderRecommendationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

