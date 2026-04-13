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


class DataLoad(Base):
    __tablename__ = "data_loads"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(32))
    rows_loaded: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)