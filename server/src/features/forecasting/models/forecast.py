from sqlalchemy import Column, Integer, Float, Date, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship
from src.db.base import Base


class Forecast(Base):
    __tablename__ = "forecasts"

    id = Column(Integer, primary_key=True)

    # Kaggle-style keys
    shop_id = Column(Integer, nullable=True, index=True)
    item_id = Column(Integer, nullable=True, index=True)
    month = Column(Date, nullable=True, index=True)
    predicted_cnt = Column(Float, nullable=True)

    # Legacy keys (совместимость с текущим API)
    product_id = Column(Integer, ForeignKey("products.id"))
    warehouse_id = Column(Integer, ForeignKey("warehouses.id"))

    forecast_date = Column(Date)  # когда создан прогноз
    target_date = Column(Date)    # на какую дату прогноз

    predicted_quantity = Column(Float)

    lower_bound = Column(Float, nullable=True)
    upper_bound = Column(Float, nullable=True)

    model_id = Column(Integer, ForeignKey("model_versions.id"))

    created_at = Column(DateTime(timezone=True), server_default=func.now())

    product = relationship("Product", back_populates="forecasts")
    warehouse = relationship("Warehouse", back_populates="forecasts")
    model_version = relationship("ModelMetadata", back_populates="forecasts")
    explanations = relationship(
        "ForecastExplanation",
        back_populates="forecast",
        cascade="all, delete-orphan",
    )