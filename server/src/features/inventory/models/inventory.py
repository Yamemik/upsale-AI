from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime, UniqueConstraint, Index
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.db.base import Base


class Inventory(Base):
    """Текущий остаток товара на складе (одна строка на пару product_id + warehouse_id)."""

    __tablename__ = "inventory"
    __table_args__ = (
        UniqueConstraint("product_id", "warehouse_id", name="uq_inventory_product_warehouse"),
        Index("ix_inventory_product_warehouse", "product_id", "warehouse_id"),
    )

    id = Column(Integer, primary_key=True)

    product_id = Column(Integer, ForeignKey("products.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))

    stock_quantity = Column(Float)

    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="inventory_rows")
    warehouse = relationship("Warehouse", back_populates="inventory_rows")


class InventoryHistory(Base):
    """История изменений остатков: снимки количества с интервалом действия (valid_from / valid_to) для аналитики и аудита."""

    __tablename__ = "inventory_history"

    id = Column(Integer, primary_key=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)
    stock_quantity = Column(Float, nullable=False)
    valid_from = Column(DateTime(timezone=True), nullable=False, server_default=func.now())
    valid_to = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())