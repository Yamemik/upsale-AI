from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Integer
from sqlalchemy.orm import Mapped, mapped_column, relationship

from src.db.base import Base


class Recommendation(Base):
    """Простая upsale/cross-sell рекомендация по товару: предлагаемое количество без привязки к складу."""

    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)

    product_id: Mapped[int] = mapped_column(ForeignKey("products.id"))

    recommended_quantity: Mapped[int]

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)

    product = relationship("Product", back_populates="recommendations")