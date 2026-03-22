from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.warehouse import Warehouse


class WarehouseRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, warehouse: Warehouse) -> Warehouse:
        self.db.add(warehouse)
        await self.db.commit()
        await self.db.refresh(warehouse)
        return warehouse

    async def get_by_id(self, warehouse_id: int) -> Warehouse | None:
        result = await self.db.execute(
            select(Warehouse).where(Warehouse.id == warehouse_id)
        )
        return result.scalar_one_or_none()

    async def get_by_external_id(self, external_id: str) -> Warehouse | None:
        result = await self.db.execute(
            select(Warehouse).where(Warehouse.external_id == external_id)
        )
        return result.scalar_one_or_none()

    async def get_or_create_by_external_id(
        self,
        external_id: str,
        name: str,
        *,
        location: str | None = None,
    ) -> Warehouse:
        existing = await self.get_by_external_id(external_id)
        if existing:
            return existing
        warehouse = Warehouse(
            external_id=external_id,
            name=name,
            location=location,
        )
        self.db.add(warehouse)
        await self.db.commit()
        await self.db.refresh(warehouse)
        return warehouse

    async def get_all(self) -> list[Warehouse]:
        result = await self.db.execute(select(Warehouse))
        return result.scalars().all()

