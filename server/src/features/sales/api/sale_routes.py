from typing import Literal

from fastapi import APIRouter, Depends, File, HTTPException, Query, UploadFile, status

from ..dependencies import (
    get_kaggle_dataset_import_service,
    get_sale_csv_import_service,
    get_sales_service,
)
from ..schemas.kaggle_import_schema import KaggleImportRunResult
from ..schemas.sale_schema import SaleCreate, SaleCsvImportResult, SaleResponse
from ..services.kaggle_dataset_import_service import STEP_ORDER, STEP_TITLE, KaggleDatasetImportService
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
            import_format: Literal["auto", "kaggle", "legacy"] = Query(
                "auto",
                description="auto: Kaggle sales_train по заголовкам; kaggle/legacy — принудительно",
            ),
            service: SaleCsvImportService = Depends(get_sale_csv_import_service),
        ):
            data = await file.read()
            result = await service.import_csv_bytes(data, import_format=import_format)
            return SaleCsvImportResult(
                imported=result["imported"],
                skipped=result["skipped"],
                errors=result["errors"],
                format_detected=result.get("format_detected"),
            )

        @self.router.get(
            "/import/kaggle/steps",
            status_code=status.HTTP_200_OK,
        )
        async def get_kaggle_import_steps():
            return [
                {"id": step, "order": i, "title": STEP_TITLE[step]}
                for i, step in enumerate(STEP_ORDER, start=1)
            ]

        @self.router.post(
            "/import/kaggle/pipeline",
            response_model=KaggleImportRunResult,
            status_code=status.HTTP_200_OK,
        )
        async def import_kaggle_pipeline(
            mode: Literal["upsert", "reload"] = Query("upsert"),
            dry_run: bool = Query(False),
            steps: str | None = Query(
                None,
                description="CSV список шагов: categories,items_ml,products,warehouses,sales,inventory",
            ),
            categories_file: UploadFile | None = File(None),
            items_file: UploadFile | None = File(None),
            shops_file: UploadFile | None = File(None),
            sales_file: UploadFile | None = File(None),
            inventory_file: UploadFile | None = File(None),
            service: KaggleDatasetImportService = Depends(get_kaggle_dataset_import_service),
        ):
            selected_steps = (
                [s.strip() for s in steps.split(",") if s.strip()] if steps else list(STEP_ORDER)
            )
            unknown = [s for s in selected_steps if s not in STEP_ORDER]
            if unknown:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"unknown steps: {', '.join(unknown)}",
                )

            try:
                return await service.run(
                    mode=mode,
                    dry_run=dry_run,
                    steps_requested=selected_steps,
                    categories_bytes=await categories_file.read() if categories_file else None,
                    items_bytes=await items_file.read() if items_file else None,
                    shops_bytes=await shops_file.read() if shops_file else None,
                    sales_bytes=await sales_file.read() if sales_file else None,
                    inventory_bytes=await inventory_file.read() if inventory_file else None,
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Ошибка импорта: {e}",
                ) from e

        @self.router.post(
            "/import/kaggle/step/{step_id}",
            response_model=KaggleImportRunResult,
            status_code=status.HTTP_200_OK,
        )
        async def import_kaggle_single_step(
            step_id: str,
            mode: Literal["upsert", "reload"] = Query("upsert"),
            dry_run: bool = Query(False),
            categories_file: UploadFile | None = File(None),
            items_file: UploadFile | None = File(None),
            shops_file: UploadFile | None = File(None),
            sales_file: UploadFile | None = File(None),
            inventory_file: UploadFile | None = File(None),
            service: KaggleDatasetImportService = Depends(get_kaggle_dataset_import_service),
        ):
            if step_id not in STEP_ORDER:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"unknown step: {step_id}",
                )
            try:
                return await service.run(
                    mode=mode,
                    dry_run=dry_run,
                    steps_requested=[step_id],
                    categories_bytes=await categories_file.read() if categories_file else None,
                    items_bytes=await items_file.read() if items_file else None,
                    shops_bytes=await shops_file.read() if shops_file else None,
                    sales_bytes=await sales_file.read() if sales_file else None,
                    inventory_bytes=await inventory_file.read() if inventory_file else None,
                )
            except Exception as e:
                raise HTTPException(
                    status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                    detail=f"Ошибка импорта: {e}",
                ) from e