from datetime import datetime, timedelta, timezone

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.synclog_model import SyncState


class SyncStateRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get_last_sync(self, entity: str) -> datetime:
        result = await self.db.execute(
            select(SyncState).where(SyncState.entity == entity)
        )
        row = result.scalar_one_or_none()
        if row is None:
            return datetime.now(timezone.utc) - timedelta(days=1)
        return row.last_sync_at

    async def update_last_sync(self, entity: str, last_sync_at: datetime) -> SyncState:
        result = await self.db.execute(
            select(SyncState).where(SyncState.entity == entity)
        )
        row = result.scalar_one_or_none()
        if row is None:
            row = SyncState(entity=entity, last_sync_at=last_sync_at)
            self.db.add(row)
        else:
            row.last_sync_at = last_sync_at
        await self.db.flush()
        return row
