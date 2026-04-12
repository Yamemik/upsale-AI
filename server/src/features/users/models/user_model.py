from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, func
from sqlalchemy.orm import relationship

from src.db.base import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    login = Column(String(128), unique=True, index=True, nullable=False)
    email = Column(String(255), unique=True, index=True, nullable=True)
    hashed_password = Column(Text, nullable=False)
    surname = Column(String(50), nullable=True)
    name = Column(String(50), nullable=True)
    patr = Column(String(50), nullable=True)
    is_admin = Column(Boolean, default=False)

    api_keys = relationship("ApiKey", back_populates="owner")
