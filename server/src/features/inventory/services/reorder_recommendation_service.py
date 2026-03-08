from ..models.reorder_recommendation import ReorderRecommendation
from ..repositories.reorder_recommendation_repository import (
    ReorderRecommendationRepository,
)
from ..schemas.reorder_recommendation_schema import (
    ReorderRecommendationCreate,
    ReorderRecommendationOut,
    ReorderRecommendationUpdate,
)


class ReorderRecommendationService:
    def __init__(self, repo: ReorderRecommendationRepository):
        self.repo = repo

    async def get_recommendations(self) -> list[ReorderRecommendationOut]:
        items = await self.repo.get_all()
        return [ReorderRecommendationOut.model_validate(item) for item in items]

    async def get_recommendation(
        self, recommendation_id: int
    ) -> ReorderRecommendationOut | None:
        item = await self.repo.get_by_id(recommendation_id)
        if not item:
            return None
        return ReorderRecommendationOut.model_validate(item)

    async def create_recommendation(
        self, data: ReorderRecommendationCreate
    ) -> ReorderRecommendationOut:
        recommendation = ReorderRecommendation(**data.model_dump())
        created = await self.repo.add(recommendation)
        return ReorderRecommendationOut.model_validate(created)

    async def update_recommendation(
        self, recommendation_id: int, data: ReorderRecommendationUpdate
    ) -> ReorderRecommendationOut | None:
        recommendation = await self.repo.get_by_id(recommendation_id)
        if not recommendation:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(recommendation, key, value)

        await self.repo.db.commit()
        await self.repo.db.refresh(recommendation)

        return ReorderRecommendationOut.model_validate(recommendation)

