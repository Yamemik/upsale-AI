from sqlalchemy import Column, Integer, Float, Date, ForeignKey
from sqlalchemy.orm import relationship
from src.db.base import Base


class Sale(Base):
    __tablename__ = "sales"

    id = Column(Integer, primary_key=True)

    product_id = Column(Integer, ForeignKey("products.id"), index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), index=True)

    sale_date = Column(Date, index=True)

    quantity = Column(Float)
    price = Column(Float)

    revenue = Column(Float)

    product = relationship("Product")
    warehouse = relationship("Warehouse")