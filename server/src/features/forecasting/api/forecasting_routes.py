from fastapi import APIRouter, Depends, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from ..services.forecasting_service import ForecastingService
from ..schemas.forecast_schema import ForecastRequest, ForecastResponse
from ..dependencies import get_forecast_service


class ForecastRoutes:
    def __init__(self):
        self.router = APIRouter(prefix="/forecast", tags=["Forecast"])
        self._register_routes()

    def _register_routes(self):
        @self.router.post(
            "/",
            response_model=ForecastResponse,
            status_code=status.HTTP_200_OK,
        )
        async def make_forecast(
            data: ForecastRequest,
            db: AsyncSession = Depends(get_db),
            service: ForecastingService = Depends(get_forecast_service)
        ):
            return await service.generate_forecast(db, data)

        @self.router.get(
            "/history",
            response_model=list[ForecastResponse],
        )
        async def get_forecast_history(
            db: AsyncSession = Depends(get_db),
            service: ForecastingService = Depends(get_forecast_service)
        ):
            return await service.get_forecast_history(db)
