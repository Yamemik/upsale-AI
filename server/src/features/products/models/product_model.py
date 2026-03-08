from sqlalchemy import Column, Integer, String, DateTime
from sqlalchemy.sql import func
from src.db.base import Base


class Product(Base):
    __tablename__ = "products"

    id = Column(Integer, primary_key=True, index=True)

    external_id = Column(String, unique=True, index=True)  # GUID из 1С
    name = Column(String, index=True)

    category = Column(String, index=True)
    brand = Column(String, nullable=True)

    created_at = Column(DateTime(timezone=True), server_default=func.now())