from datetime import date
from pydantic import BaseModel


class SaleBase(BaseModel):
    product_id: str
    product_name: str
    category: str
    warehouse_id: str
    sale_date: date
    quantity: float
    price: float
    revenue: float


class SaleCreate(SaleBase):
    pass


class SaleResponse(SaleBase):
    id: int

    class Config:
        from_attributes = True
