from fastapi import APIRouter

from src.features.users.api.user_routes import UserRoutes
from src.features.users.api.auth_routes import AuthRoutes
from src.features.sales.api.sale_routes import SaleRoutes
from src.features.forecasting.api.forecasting_routes import ForecastRoutes
from src.features.integration_1s.api.integration1S_routes import Integration1SRoutes


api_router = APIRouter(prefix="/api/v1")

# создаём экземпляры классов и подключаем их роутеры
api_router.include_router(AuthRoutes().router)
api_router.include_router(UserRoutes().router)
api_router.include_router(SaleRoutes().router)
api_router.include_router(ForecastRoutes().router)
api_router.include_router(Integration1SRoutes().router)