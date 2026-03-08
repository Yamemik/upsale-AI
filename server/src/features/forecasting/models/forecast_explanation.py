from sqlalchemy import Column, Integer, Float, String, ForeignKey
from src.db.base import Base


class ForecastExplanation(Base):
    __tablename__ = "forecast_explanations"

    id = Column(Integer, primary_key=True)

    forecast_id = Column(Integer, ForeignKey("forecasts.id"))

    feature_name = Column(String)
    feature_value = Column(Float)

    shap_value = Column(Float)