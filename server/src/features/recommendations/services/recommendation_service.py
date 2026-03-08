from ..models.recommendation_model import Recommendation
from ..repositories.recommendation_repository import RecommendationRepository
from ..schemas.recommendation_schema import (
    RecommendationCreate,
    RecommendationOut,
    RecommendationUpdate,
)


class RecommendationService:
    def __init__(self, repo: RecommendationRepository):
        self.repo = repo

    async def get_recommendations(self) -> list[RecommendationOut]:
        items = await self.repo.get_all()
        return [RecommendationOut.model_validate(item) for item in items]

    async def get_recommendation(
        self, recommendation_id: int
    ) -> RecommendationOut | None:
        item = await self.repo.get_by_id(recommendation_id)
        if not item:
            return None
        return RecommendationOut.model_validate(item)

    async def create_recommendation(
        self, data: RecommendationCreate
    ) -> RecommendationOut:
        recommendation = Recommendation(**data.model_dump())
        created = await self.repo.add(recommendation)
        return RecommendationOut.model_validate(created)

    async def update_recommendation(
        self, recommendation_id: int, data: RecommendationUpdate
    ) -> RecommendationOut | None:
        recommendation = await self.repo.get_by_id(recommendation_id)
        if not recommendation:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(recommendation, key, value)

        await self.repo.db.commit()
        await self.repo.db.refresh(recommendation)

        return RecommendationOut.model_validate(recommendation)

