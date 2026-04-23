from fastapi import APIRouter, Depends, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db

from ..dependencies import get_api_key
from ..models.apikey_model import ApiKey
from ..repositories.sync_state_repository import SyncStateRepository
from ..schemas.sync_schema import (
    IncrementalImportRequest,
    SyncLastDateResponse,
    SyncUpdateDateRequest,
)
from ..services.incremental_import_service import import_incremental_sales


class Integration1SPublicRoutes:
    def __init__(self):
        self.router = APIRouter(tags=["1C sync"])
        self._register_routes()

    def _register_routes(self):
        @self.router.get(
            "/sync/last-date",
            response_model=SyncLastDateResponse,
            status_code=status.HTTP_200_OK,
        )
        async def get_last_sync_date(
            entity: str = Query("sales"),
            api_key: ApiKey = Depends(get_api_key),
            db: AsyncSession = Depends(get_db),
        ):
            repo = SyncStateRepository(db)
            return SyncLastDateResponse(last_sync_at=await repo.get_last_sync(entity))

        @self.router.post(
            "/sync/update-date",
            response_model=SyncLastDateResponse,
            status_code=status.HTTP_200_OK,
        )
        async def update_sync_date(
            body: SyncUpdateDateRequest,
            api_key: ApiKey = Depends(get_api_key),
            db: AsyncSession = Depends(get_db),
        ):
            async with db.begin():
                row = await SyncStateRepository(db).update_last_sync(body.entity, body.last_sync_at)
            return SyncLastDateResponse(last_sync_at=row.last_sync_at)

        @self.router.post(
            "/import/incremental",
            status_code=status.HTTP_200_OK,
        )
        async def import_incremental(
            body: IncrementalImportRequest,
            api_key: ApiKey = Depends(get_api_key),
            db: AsyncSession = Depends(get_db),
        ):
            return await import_incremental_sales(db, body)
