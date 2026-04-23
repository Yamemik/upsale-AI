from datetime import datetime

from sqlalchemy import DateTime, String
from sqlalchemy.orm import Mapped, mapped_column

from src.db.base import Base


class SyncLog(Base):
    """Журнал синхронизации с внешними системами: источник, сущность, статус и текстовое сообщение об ошибке или результате."""

    __tablename__ = "sync_logs"

    id: Mapped[int] = mapped_column(primary_key=True)

    system: Mapped[str]
    entity: Mapped[str]
    status: Mapped[str]
    message: Mapped[str | None]

    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class DataLoad(Base):
    """Учёт массовых загрузок данных: источник, статус и число загруженных строк для мониторинга импортов."""

    __tablename__ = "data_loads"

    id: Mapped[int] = mapped_column(primary_key=True)
    source: Mapped[str] = mapped_column(String(100))
    status: Mapped[str] = mapped_column(String(32))
    rows_loaded: Mapped[int] = mapped_column(default=0)
    created_at: Mapped[datetime] = mapped_column(default=datetime.utcnow)


class SyncState(Base):
    """Текущее состояние инкрементальной синхронизации по сущности."""

    __tablename__ = "sync_state"

    id: Mapped[int] = mapped_column(primary_key=True)
    entity: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    last_sync_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
