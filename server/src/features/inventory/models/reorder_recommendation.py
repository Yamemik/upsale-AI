from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.sql import func
from src.db.base import Base


class ReorderRecommendation(Base):
    __tablename__ = "reorder_recommendations"

    id = Column(Integer, primary_key=True)

    product_id = Column(Integer, ForeignKey("products.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))

    recommended_quantity = Column(Float)

    reorder_point = Column(Float)

    lead_time_days = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())