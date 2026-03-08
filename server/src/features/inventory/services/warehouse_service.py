from ..models.warehouse import Warehouse
from ..repositories.warehouse_repository import WarehouseRepository
from ..schemas.warehouse_schema import (
    WarehouseCreate,
    WarehouseOut,
    WarehouseUpdate,
)


class WarehouseService:
    def __init__(self, repo: WarehouseRepository):
        self.repo = repo

    async def get_warehouses(self) -> list[WarehouseOut]:
        items = await self.repo.get_all()
        return [WarehouseOut.model_validate(item) for item in items]

    async def get_warehouse(self, warehouse_id: int) -> WarehouseOut | None:
        item = await self.repo.get_by_id(warehouse_id)
        if not item:
            return None
        return WarehouseOut.model_validate(item)

    async def create_warehouse(self, data: WarehouseCreate) -> WarehouseOut:
        warehouse = Warehouse(**data.model_dump())
        created = await self.repo.add(warehouse)
        return WarehouseOut.model_validate(created)

    async def update_warehouse(
        self, warehouse_id: int, data: WarehouseUpdate
    ) -> WarehouseOut | None:
        warehouse = await self.repo.get_by_id(warehouse_id)
        if not warehouse:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(warehouse, key, value)

        await self.repo.db.commit()
        await self.repo.db.refresh(warehouse)

        return WarehouseOut.model_validate(warehouse)

