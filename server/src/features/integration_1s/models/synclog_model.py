from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class SyncLog(Base):
    __tablename__ = "sync_logs"

    id: Mapped[int] = mapped_column(primary_key=True)

    system: Mapped[str]
    entity: Mapped[str]
    status: Mapped[str]
    message: Mapped[str | None]

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)