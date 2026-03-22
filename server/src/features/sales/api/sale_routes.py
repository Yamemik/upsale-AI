from fastapi import APIRouter, Depends, File, UploadFile, status

from ..dependencies import get_sale_csv_import_service, get_sales_service
from ..schemas.sale_schema import SaleCreate, SaleCsvImportResult, SaleResponse
from ..services.sale_csv_import_service import SaleCsvImportService
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

        @self.router.post(
            "/import/csv",
            response_model=SaleCsvImportResult,
            status_code=status.HTTP_200_OK,
        )
        async def import_sales_csv(
            file: UploadFile = File(...),
            service: SaleCsvImportService = Depends(get_sale_csv_import_service),
        ):
            data = await file.read()
            result = await service.import_csv_bytes(data)
            return SaleCsvImportResult(
                imported=result["imported"],
                skipped=result["skipped"],
                errors=result["errors"],
            )