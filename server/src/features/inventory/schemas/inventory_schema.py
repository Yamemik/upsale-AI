from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class InventoryBase(BaseModel):
    product_id: int
    warehouse_id: int
    stock_quantity: float


class InventoryCreate(InventoryBase):
    pass


class InventoryUpdate(BaseModel):
    stock_quantity: Optional[float] = None


class InventoryOut(InventoryBase):
    id: int
    updated_at: datetime

    class Config:
        from_attributes = True

