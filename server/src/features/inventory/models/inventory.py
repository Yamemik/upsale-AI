from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.db.base import Base


class Inventory(Base):
    __tablename__ = "inventory"

    id = Column(Integer, primary_key=True)

    product_id = Column(Integer, ForeignKey("products.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))

    stock_quantity = Column(Float)

    updated_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="inventory_rows")
    warehouse = relationship("Warehouse", back_populates="inventory_rows")