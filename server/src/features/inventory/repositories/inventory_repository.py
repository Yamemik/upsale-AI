from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.inventory import Inventory


class InventoryRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, inventory: Inventory) -> Inventory:
        self.db.add(inventory)
        await self.db.commit()
        await self.db.refresh(inventory)
        return inventory

    async def get_by_id(self, inventory_id: int) -> Inventory | None:
        result = await self.db.execute(
            select(Inventory).where(Inventory.id == inventory_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Inventory]:
        result = await self.db.execute(select(Inventory))
        return result.scalars().all()

