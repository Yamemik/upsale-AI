from datetime import date
from pydantic import BaseModel


class SaleBase(BaseModel):
    product_id: int
    warehouse_id: int
    sale_date: date
    quantity: float
    price: float
    revenue: float | None = None


class SaleCreate(SaleBase):
    pass


class SaleResponse(SaleBase):
    id: int
    product_name: str | None = None
    category: str | None = None

    class Config:
        from_attributes = True


class SaleCsvImportResult(BaseModel):
    imported: int
    skipped: int
    errors: list[str]
    format_detected: str | None = None
