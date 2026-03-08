from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ..models.forecast import Forecast


class ForecastRepository:
    def __init__(self, db: AsyncSession):
        self.db = db

    async def add(self, forecast: Forecast) -> Forecast:
        self.db.add(forecast)
        await self.db.commit()
        await self.db.refresh(forecast)
        return forecast

    async def get_by_id(self, forecast_id: int) -> Forecast | None:
        result = await self.db.execute(
            select(Forecast).where(Forecast.id == forecast_id)
        )
        return result.scalar_one_or_none()

    async def get_all(self) -> list[Forecast]:
        result = await self.db.execute(select(Forecast))
        return result.scalars().all()

