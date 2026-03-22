from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.product_model import Product


class ProductRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, product: Product) -> Product:
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def get_by_id(self, product_id: int) -> Product | None:
        result = await self.db.execute(
            select(Product).where(Product.id == product_id)
        )
        return result.scalar_one_or_none()

    async def get_by_external_id(self, external_id: str) -> Product | None:
        result = await self.db.execute(
            select(Product).where(Product.external_id == external_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create_by_external_id(
        self,
        external_id: str,
        name: str,
        *,
        category: str = "",
    ) -> Product:
        existing = await self.get_by_external_id(external_id)
        if existing:
            return existing
        product = Product(
            external_id=external_id,
            name=name,
            category=category,
        )
        self.db.add(product)
        await self.db.commit()
        await self.db.refresh(product)
        return product

    async def get_all(self) -> list[Product]:
        result = await self.db.execute(select(Product))
        return result.scalars().all()

