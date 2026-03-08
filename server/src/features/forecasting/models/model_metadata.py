from sqlalchemy import Column, Integer, String, Float, DateTime
from sqlalchemy.sql import func
from src.db.base import Base


class ModelMetadata(Base):
    __tablename__ = "models"

    id = Column(Integer, primary_key=True)

    name = Column(String)
    version = Column(String)

    algorithm = Column(String)

    mape = Column(Float)
    rmse = Column(Float)

    model_path = Column(String)

    trained_at = Column(DateTime(timezone=True), server_default=func.now())