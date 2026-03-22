from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.model_metadata import ModelMetadata


class ModelMetadataRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, meta: ModelMetadata) -> ModelMetadata:
        self.db.add(meta)
        await self.db.commit()
        await self.db.refresh(meta)
        return meta

    async def get_latest(self) -> ModelMetadata | None:
        result = await self.db.execute(
            select(ModelMetadata).order_by(ModelMetadata.id.desc()).limit(1)
        )
        return result.scalar_one_or_none()
