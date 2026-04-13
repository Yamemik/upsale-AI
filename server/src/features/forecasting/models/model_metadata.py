from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from src.db.base import Base


class ModelMetadata(Base):
    __tablename__ = "model_versions"

    id = Column(Integer, primary_key=True)

    name = Column(String)
    version = Column(String)

    algorithm = Column(String)

    mape = Column(Float)
    rmse = Column(Float)

    model_path = Column(String)
    is_active = Column(Boolean, nullable=False, default=True)

    trained_at = Column(DateTime(timezone=True), server_default=func.now())

    forecasts = relationship("Forecast", back_populates="model_version")