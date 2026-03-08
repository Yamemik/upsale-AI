from sqlalchemy import Column, Integer, String
from src.db.base import Base


class Warehouse(Base):
    __tablename__ = "warehouses"

    id = Column(Integer, primary_key=True, index=True)

    external_id = Column(String, unique=True, index=True)
    name = Column(String)

    location = Column(String, nullable=True)