from sqlalchemy import Column, Integer, Date, ForeignKey, DateTime, Numeric, UniqueConstraint
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.db.base import Base


class Forecast(Base):
    __tablename__ = "forecasts"
    __table_args__ = (
        UniqueConstraint(
            "product_id",
            "warehouse_id",
            "target_date",
            "model_id",
            name="uq_forecasts_product_warehouse_target_model",
        ),
    )

    id = Column(Integer, primary_key=True)

    shop_id = Column(Integer, ForeignKey("shops.shop_id"), nullable=True, index=True)
    item_id = Column(Integer, ForeignKey("items.item_id"), nullable=True, index=True)
    product_id = Column(Integer, ForeignKey("products.id"), nullable=False, index=True)
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"), nullable=False, index=True)

    forecast_date = Column(Date)  # когда создан прогноз
    target_date = Column(Date, nullable=False, index=True)    # на какую дату прогноз

    predicted_quantity = Column(Numeric(14, 3), nullable=False)

    lower_bound = Column(Numeric(14, 3), nullable=True)
    upper_bound = Column(Numeric(14, 3), nullable=True)

    model_id = Column(Integer, ForeignKey("model_versions.id"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="forecasts")
    warehouse = relationship("Warehouse", back_populates="forecasts")
    model_version = relationship("ModelMetadata", back_populates="forecasts")
    explanations = relationship(
        "ForecastExplanation",
        back_populates="forecast",
        cascade="all, delete-orphan",
    )