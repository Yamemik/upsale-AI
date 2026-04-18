from sqlalchemy import Column, Integer, String, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.base import Base


class Product(Base):
    """Товар в операционной модели: связь с 1С (external_id), категория, бренд, опциональная связь с Item из ML-слоя.

    Центральная сущность для продаж, остатков, прогнозов и рекомендаций.
    """

    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    external_id = Column(String, unique=True, index=True)  # GUID из 1С
    name = Column(String, index=True)

    category = Column(String, index=True)
    brand = Column(String, nullable=True)
    item_id = Column(Integer, ForeignKey("items.item_id", ondelete="SET NULL"), nullable=True, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    sales = relationship("Sale", back_populates="product")
    forecasts = relationship("Forecast", back_populates="product")
    inventory_rows = relationship("Inventory", back_populates="product")
    reorder_recommendations = relationship("ReorderRecommendation", back_populates="product")
    recommendations = relationship("Recommendation", back_populates="product")