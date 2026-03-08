from sqlalchemy import select
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

