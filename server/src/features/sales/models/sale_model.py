from sqlalchemy import Column, Integer, Float, Date, ForeignKey, JSON, Computed, Index
from sqlalchemy.orm import relationship
from src.db.base import Base


class Sale(Base):
    """Факт продажи: товар, склад, дата, количество и цена; выручка хранится как вычисляемое поле.

    Поле import_extras — временное хранилище признаков при импорте из датасетов до нормализации схемы.
    """

    __tablename__ = "sales"
    __table_args__ = (
        Index("ix_sales_sale_date", "sale_date"),
        Index("ux_sales_date_warehouse_product", "sale_date", "warehouse_id", "product_id", unique=True),
    )

    id = Column(Integer, primary_key=True)

    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), index=True)

    sale_date = Column(Date, index=True)

    quantity = Column(Float)
    price = Column(Float)

    revenue = Column(Float, Computed("quantity * price", persisted=True))

    # Признаки из датасета ВКР (lag, rolling, stock_level и т.д.) до выделения колонок в схеме
    import_extras = Column(JSON, nullable=True)

    product = relationship("Product", back_populates="sales")
    warehouse = relationship("Warehouse", back_populates="sales")