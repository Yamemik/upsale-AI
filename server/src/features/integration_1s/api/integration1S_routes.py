from fastapi import APIRouter, Depends

from ..dependencies import get_api_key
from ..models.apikey_model import ApiKey
from ..services.sync_service import SyncService
from ..client.odata_client import ODataClient
from src.config.settings import settings


class Integration1SRoutes:
    def __init__(self):
        self.router = APIRouter(
            prefix="/integration/1c",
            tags=["1C integration"],
        )
        self._register_routes()

    def _register_routes(self):
        @self.router.post("/sync-sales")
        async def sync_sales(
            api_key: ApiKey = Depends(get_api_key),
        ):
            # Инициализируем клиента и сервис синхронизации.
            client = ODataClient(
                base_url=settings.INTEGRATION_1C_BASE_URL,
                username=settings.INTEGRATION_1C_USERNAME,
                password=settings.INTEGRATION_1C_PASSWORD,
            )
            service = SyncService(client)

            sales_data = await service.sync_sales()

            return {
                "status": "sync completed",
                "synced_count": len(sales_data),
            }
