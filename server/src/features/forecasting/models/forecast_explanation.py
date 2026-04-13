from sqlalchemy import Column, Integer, Float, String, ForeignKey, DateTime
from sqlalchemy.sql import func
from sqlalchemy.orm import relationship

from src.db.base import Base


class ForecastExplanation(Base):
    __tablename__ = "forecast_explanations"

    id = Column(Integer, primary_key=True)

    forecast_id = Column(Integer, ForeignKey("forecasts.id", ondelete="CASCADE"), index=True)

    feature_name = Column(String)
    feature_value = Column(Float)

    shap_value = Column(Float)
    created_at = Column(DateTime(timezone=True), server_default=func.now())

    forecast = relationship("Forecast", back_populates="explanations")