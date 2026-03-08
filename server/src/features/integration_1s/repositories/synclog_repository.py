from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.synclog_model import SyncLog


class SyncLogRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, log: SyncLog) -> SyncLog:
        self.db.add(log)
        await self.db.commit()
        await self.db.refresh(log)
        return log

    async def get_by_id(self, log_id: int) -> SyncLog | None:
        result = await self.db.execute(
            select(SyncLog).where(SyncLog.id == log_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[SyncLog]:
        result = await self.db.execute(select(SyncLog))
        return result.scalars().all()

