from datetime import date

from sqlalchemy import func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.sale_model import Sale


class SalesRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def create(self, sale: Sale) -> Sale:
        self.db.add(sale)
        await self.db.commit()
        await self.db.refresh(sale)
        return sale

    async def get_all(self) -> list[Sale]:
        result = await self.db.execute(select(Sale))
        return result.scalars().all()

    async def get_by_product(self, product_id: int) -> list[Sale]:
        result = await self.db.execute(
            select(Sale).where(Sale.product_id == product_id)
        )
        return result.scalars().all()

    async def get_by_product_and_warehouse(
        self,
        product_id: int,
        warehouse_id: int | None,
    ) -> list[Sale]:
        q = select(Sale).where(Sale.product_id == product_id)
        if warehouse_id is not None:
            q = q.where(Sale.warehouse_id == warehouse_id)
        result = await self.db.execute(q)
        return result.scalars().all()

    async def count(self) -> int:
        result = await self.db.execute(select(func.count()).select_from(Sale))
        return int(result.scalar_one())

    async def max_sale_date(self) -> date | None:
        result = await self.db.execute(select(func.max(Sale.sale_date)))
        return result.scalar_one_or_none()

    async def add_all(self, sales: list[Sale]) -> None:
        self.db.add_all(sales)
        await self.db.commit()
