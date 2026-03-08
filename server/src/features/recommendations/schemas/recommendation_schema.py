from datetime import datetime

from pydantic import BaseModel


class RecommendationBase(BaseModel):
    product_id: int
    recommended_quantity: int


class RecommendationCreate(RecommendationBase):
    pass


class RecommendationUpdate(BaseModel):
    recommended_quantity: int | None = None


class RecommendationOut(RecommendationBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True

