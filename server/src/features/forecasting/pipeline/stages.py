"""
Эталонный порядок загрузки CSV (Kaggle Predict Future Sales):

1) item_categories.csv -> categories
2) items.csv -> items (ML слой)
3) items.csv -> products (бизнес слой)
4) shops.csv -> warehouses
5) sales_train.csv -> sales (история)
6) inventory.csv (или расчетный снимок) -> inventory (остатки)
"""

from enum import Enum


class PipelineStage(str, Enum):
    LOAD_CATEGORIES = "load_categories_csv"
    LOAD_ITEMS_ML = "load_items_ml_csv"
    LOAD_PRODUCTS_BUSINESS = "load_products_business_csv"
    LOAD_WAREHOUSES = "load_warehouses_csv"
    LOAD_SALES_HISTORY = "load_sales_history_csv"
    LOAD_INVENTORY = "load_inventory_csv"


PIPELINE_DESCRIPTION: list[tuple[PipelineStage, str]] = [
    (PipelineStage.LOAD_CATEGORIES, "1. categories <- item_categories.csv"),
    (PipelineStage.LOAD_ITEMS_ML, "2. items (ML слой) <- items.csv"),
    (PipelineStage.LOAD_PRODUCTS_BUSINESS, "3. products (бизнес слой) <- items.csv"),
    (PipelineStage.LOAD_WAREHOUSES, "4. warehouses <- shops.csv"),
    (PipelineStage.LOAD_SALES_HISTORY, "5. sales (история) <- sales_train.csv"),
    (PipelineStage.LOAD_INVENTORY, "6. inventory (остатки) <- inventory.csv/расчет"),
]
