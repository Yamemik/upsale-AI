from fastapi import APIRouter, Depends, status

from ..dependencies import get_sales_service
from ..schemas.sale_schema import SaleCreate, SaleResponse
from ..services.sale_service import SaleService


class SaleRoutes:
    def __init__(self):
        self.router = APIRouter(prefix="/sales", tags=["Sales"])
        self._register_routes()

    def _register_routes(self):
        @self.router.post(
            "/",
            response_model=SaleResponse,
            status_code=status.HTTP_201_CREATED,
        )
        async def create_sale(
            data: SaleCreate,
            service: SaleService = Depends(get_sales_service),
        ):
            return await service.create_sale(data)

        @self.router.get(
            "/",
            response_model=list[SaleResponse],
        )
        async def get_sales(
            service: SaleService = Depends(get_sales_service),
        ):
            return await service.get_sales()