from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.recommendation_model import Recommendation


class RecommendationRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, recommendation: Recommendation) -> Recommendation:
        self.db.add(recommendation)
        await self.db.commit()
        await self.db.refresh(recommendation)
        return recommendation

    async def get_by_id(self, recommendation_id: int) -> Recommendation | None:
        result = await self.db.execute(
            select(Recommendation).where(Recommendation.id == recommendation_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Recommendation]:
        result = await self.db.execute(select(Recommendation))
        return result.scalars().all()

