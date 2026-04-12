from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from src.db.base import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)

    external_id = Column(String, unique=True, index=True)
    name = Column(String)

    location = Column(String, nullable=True)

    sales = relationship("Sale", back_populates="warehouse")
    forecasts = relationship("Forecast", back_populates="warehouse")
    inventory_rows = relationship("Inventory", back_populates="warehouse")
    reorder_recommendations = relationship("ReorderRecommendation", back_populates="warehouse")