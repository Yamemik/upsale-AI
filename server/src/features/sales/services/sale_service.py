from ..models.sale_model import Sale
from ..repositories.sale_repository import SalesRepository
from ..schemas.sale_schema import SaleCreate


class SaleService:
    def __init__(self, repo: SalesRepository):
        self.repo = repo

    async def create_sale(self, data: SaleCreate) -> Sale:
        sale = Sale(**data.model_dump())
        return await self.repo.create(sale)

    async def get_sales(self) -> list[Sale]:
        return await self.repo.get_all()

    async def get_sales_by_product(self, product_id: int) -> list[Sale]:
        return await self.repo.get_by_product(product_id)
