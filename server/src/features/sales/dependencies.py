from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from src.features.sales.repositories.sale_repository import SalesRepository
from src.features.sales.services.sale_service import SaleService


def get_sales_repository(
    db: AsyncSession = Depends(get_db),
) -> SalesRepository:
    return SalesRepository(db)


def get_sales_service(
    repo: SalesRepository = Depends(get_sales_repository),
) -> SaleService:
    return SaleService(repo)