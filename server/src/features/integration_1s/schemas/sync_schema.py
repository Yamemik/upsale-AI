from datetime import date, datetime

from pydantic import BaseModel, Field


class SyncLastDateResponse(BaseModel):
    last_sync_at: datetime


class SyncUpdateDateRequest(BaseModel):
    entity: str = Field(min_length=1, default="sales")
    last_sync_at: datetime


class IncrementalSaleRow(BaseModel):
    date: date
    date_block_num: int | None = None
    shop_id: str | None = None
    shop_name: str | None = None
    item_category_id: str | None = None
    item_category_name: str | None = None
    item_id: str | None = None
    item_name: str | None = None
    item_price: float | None = 0.0
    item_cnt_day: float | None = 0.0


class IncrementalImportRequest(BaseModel):
    sales: list[IncrementalSaleRow]
