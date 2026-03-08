from ..models.product_model import Product
from ..repositories.product_repository import ProductRepository
from ..schemas.product_schema import ProductCreate, ProductOut, ProductUpdate


class ProductService:
    def __init__(self, repo: ProductRepository):
        self.repo = repo

    async def get_products(self) -> list[ProductOut]:
        items = await self.repo.get_all()
        return [ProductOut.model_validate(item) for item in items]

    async def get_product(self, product_id: int) -> ProductOut | None:
        item = await self.repo.get_by_id(product_id)
        if not item:
            return None
        return ProductOut.model_validate(item)

    async def get_product_by_external_id(
        self, external_id: str
    ) -> ProductOut | None:
        item = await self.repo.get_by_external_id(external_id)
        if not item:
            return None
        return ProductOut.model_validate(item)

    async def create_product(self, data: ProductCreate) -> ProductOut:
        product = Product(**data.model_dump())
        created = await self.repo.add(product)
        return ProductOut.model_validate(created)

    async def update_product(
        self, product_id: int, data: ProductUpdate
    ) -> ProductOut | None:
        product = await self.repo.get_by_id(product_id)
        if not product:
            return None

        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(product, key, value)

        await self.repo.db.commit()
        await self.repo.db.refresh(product)

        return ProductOut.model_validate(product)

