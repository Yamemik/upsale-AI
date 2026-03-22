from sqlalchemy import Column, Integer, Float, Date, ForeignKey, JSON
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

    # Признаки из датасета ВКР (lag, rolling, stock_level и т.д.) до выделения колонок в схеме
    import_extras = Column(JSON, nullable=True)

    product = relationship("Product")
    warehouse = relationship("Warehouse")