from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.features.sales.repositories.sale_repository import SalesRepository
from src.features.sales.services.kaggle_dataset_import_service import (
    KaggleDatasetImportService,
)
from src.features.sales.services.sale_csv_import_service import SaleCsvImportService
from src.features.sales.services.sale_service import SaleService


def get_sales_repository(
    db: AsyncSession = Depends(get_db),
) -> SalesRepository:
    return SalesRepository(db)


def get_sales_service(
    repo: SalesRepository = Depends(get_sales_repository),
) -> SaleService:
    return SaleService(repo)


def get_sale_csv_import_service(
    db: AsyncSession = Depends(get_db),
) -> SaleCsvImportService:
    return SaleCsvImportService(db)


def get_kaggle_dataset_import_service(
    db: AsyncSession = Depends(get_db),
) -> KaggleDatasetImportService:
    return KaggleDatasetImportService(db)