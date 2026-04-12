from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from src.db.base import Base


class ApiKey(Base):
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key_hash = Column(String(64), unique=True, index=True, nullable=False)  # Хеш ключа
    name = Column(String(100), nullable=False)  # Имя ключа (напр. "1C_Warehouse")
    owner_id = Column(Integer, ForeignKey("users.id"), nullable=True)  # Владелец (если есть)
    is_active = Column(Boolean, default=True)
    permissions = Column(String(50), default="read")  # read, write, admin
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    last_used_at = Column(DateTime(timezone=True), nullable=True)

    owner = relationship("User", back_populates="api_keys")