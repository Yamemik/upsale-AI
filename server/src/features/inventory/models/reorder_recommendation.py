from sqlalchemy import Column, Integer, Float, ForeignKey, DateTime
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.base import Base


class ReorderRecommendation(Base):
    """Рекомендация по пополнению запаса: объём заказа, точка перезаказа и lead time для пары товар–склад."""

    __tablename__ = "reorder_recommendations"

    id = Column(Integer, primary_key=True)

    product_id = Column(Integer, ForeignKey("products.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))

    recommended_quantity = Column(Float)

    reorder_point = Column(Float)

    lead_time_days = Column(Integer)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="reorder_recommendations")
    warehouse = relationship("Warehouse", back_populates="reorder_recommendations")