from ..models.inventory import Inventory
from ..repositories.inventory_repository import InventoryRepository
from ..schemas.inventory_schema import (
    InventoryCreate,
    InventoryOut,
    InventoryUpdate,
)


class InventoryService:
    def __init__(self, repo: InventoryRepository):
        self.repo = repo

    async def get_inventory(self) -> list[InventoryOut]:
        items = await self.repo.get_all()
        return [InventoryOut.model_validate(item) for item in items]

    async def get_inventory_item(self, inventory_id: int) -> InventoryOut | None:
        item = await self.repo.get_by_id(inventory_id)
        if not item:
            return None
        return InventoryOut.model_validate(item)

    async def create_inventory_item(
        self, data: InventoryCreate
    ) -> InventoryOut:
        inventory = Inventory(**data.model_dump())
        created = await self.repo.add(inventory)
        return InventoryOut.model_validate(created)

    async def update_inventory_item(
        self, inventory_id: int, data: InventoryUpdate
    ) -> InventoryOut | None:
        inventory = await self.repo.get_by_id(inventory_id)
        if not inventory:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(inventory, key, value)

        await self.repo.db.commit()
        await self.repo.db.refresh(inventory)

        return InventoryOut.model_validate(inventory)

