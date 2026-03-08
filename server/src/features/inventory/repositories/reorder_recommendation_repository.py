from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.reorder_recommendation import ReorderRecommendation


class ReorderRecommendationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(
        self, recommendation: ReorderRecommendation
    ) -> ReorderRecommendation:
        self.db.add(recommendation)
        await self.db.commit()
        await self.db.refresh(recommendation)
        return recommendation

    async def get_by_id(
        self, recommendation_id: int
    ) -> ReorderRecommendation | None:
        result = await self.db.execute(
            select(ReorderRecommendation).where(
                ReorderRecommendation.id == recommendation_id
            )
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[ReorderRecommendation]:
        result = await self.db.execute(select(ReorderRecommendation))
        return result.scalars().all()

