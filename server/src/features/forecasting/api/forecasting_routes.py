from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.features.forecasting.pipeline.stages import PIPELINE_DESCRIPTION, PipelineStage
from ..dependencies import get_forecast_service
from ..schemas.forecast_schema import (
    ForecastRequest,
    ForecastResponse,
    TrainFromDbRequest,
    TrainFromDbResponse,
)
from ..services.forecasting_service import ForecastingService


class ForecastRoutes:
    def __init__(self):
        self.router = APIRouter(prefix="/forecast", tags=["Forecast"])
        self._register_routes()

    def _register_routes(self):
        @self.router.get(
            "/pipeline",
            summary="Этапы конвейера (схема 1С → … → 1С)",
        )
        async def get_pipeline_schema():
            return [
                {
                    "id": stage.value,
                    "order": i,
                    "title": title,
                }
                for i, (stage, title) in enumerate(PIPELINE_DESCRIPTION, start=1)
            ]

        @self.router.get(
            "/pipeline/stages-enum",
            summary="Идентификаторы этапов (enum)",
        )
        async def get_pipeline_stage_ids():
            return [s.value for s in PipelineStage]

        @self.router.post(
            "/train",
            response_model=TrainFromDbResponse,
            status_code=status.HTTP_200_OK,
        )
        async def train_from_sales_history(
            body: TrainFromDbRequest,
            db: AsyncSession = Depends(get_db),
            service: ForecastingService = Depends(get_forecast_service),
        ):
            try:
                return await service.train_from_db(
                    db,
                    body.product_id,
                    body.warehouse_id,
                )
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e),
                ) from e

        @self.router.post(
            "/",
            response_model=ForecastResponse,
            status_code=status.HTTP_200_OK,
        )
        async def make_forecast(
            data: ForecastRequest,
            db: AsyncSession = Depends(get_db),
            service: ForecastingService = Depends(get_forecast_service),
        ):
            try:
                return await service.generate_forecast(db, data)
            except ValueError as e:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=str(e),
                ) from e
            except FileNotFoundError as e:
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail=str(e),
                ) from e

        @self.router.get(
            "/history",
            response_model=list[ForecastResponse],
        )
        async def get_forecast_history(
            db: AsyncSession = Depends(get_db),
            service: ForecastingService = Depends(get_forecast_service),
        ):
            return await service.get_forecast_history(db)
