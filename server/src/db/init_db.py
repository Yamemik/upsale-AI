import logging
from urllib.parse import urlparse

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import engine, AsyncSessionLocal

logger = logging.getLogger(__name__)
from src.db.base import Base
from src.db.init_superuser import create_superuser_if_not_exists
from src.features.sales.services.sale_csv_import_service import (
    run_sales_csv_seed_if_configured,
)
from src.db.run_migrations import run_migrations_if_needed
from src.config.settings import settings
from src.features.users.models import user_model as _user_models  # noqa: F401
from src.features.forecasting.models import forecast as _forecast_models  # noqa: F401
from src.features.forecasting.models import forecast_explanation as _forecast_expl_models  # noqa: F401
from src.features.forecasting.models import kaggle_entities as _kaggle_models  # noqa: F401
from src.features.forecasting.models import model_metadata as _model_meta_models  # noqa: F401
from src.features.integration_1s.models import apikey_model as _apikey_models  # noqa: F401
from src.features.integration_1s.models import synclog_model as _synclog_models  # noqa: F401
from src.features.inventory.models import warehouse as _warehouse_models  # noqa: F401
from src.features.products.models import product_model as _product_models  # noqa: F401
from src.features.inventory.models import inventory as _inventory_models  # noqa: F401
from src.features.inventory.models import reorder_recommendation as _reorder_models  # noqa: F401
from src.features.recommendations.models import recommendation_model as _rec_models  # noqa: F401
from src.features.sales.models import sale_model as _sale_models  # noqa: F401


def _db_connection_hint() -> str:
    try:
        u = urlparse(settings.DATABASE_URL.replace("postgresql+asyncpg://", "postgresql://", 1))
        host = u.hostname or "?"
        port = u.port or 5432
        db = (u.path or "/").lstrip("/") or "?"
        safe = f"{u.scheme}://{u.username or ''}:***@{host}:{port}/{db}"
    except Exception:
        safe = "(не удалось разобрать DATABASE_URL)"
    return (
        "\n\n=== Ошибка подключения к PostgreSQL ===\n"
        f"Строка (без пароля): {safe}\n\n"
        "Проверьте:\n"
        "  • Служба PostgreSQL запущена, порт совпадает с DATABASE_URL.\n"
        "  • База существует (например scripts/create_udsale_db.sql или docker compose up db).\n"
        "  • Логин и пароль в .env верные.\n"
        "При WinError 10054 / «connection was closed» на локальной машине добавьте в .env:\n"
        "  DATABASE_SSL_DISABLE=true\n"
    )


async def init_db():
    """Инициализация БД:
    - При первом запуске (без Alembic) → create_all
    - При наличии Alembic → проверка и выполнение миграций (если разрешено)
    - Создание суперюзера
    """

    alembic_present = False

    try:
        # Проверка наличия alembic_version
        async with engine.begin() as conn:
            result = await conn.execute(text("SELECT to_regclass('public.alembic_version')"))
            alembic_present = bool(result.scalar())

            if not alembic_present:
                await conn.run_sync(Base.metadata.create_all)
                print("✅ Таблицы созданы через create_all (первый запуск).")
    except Exception as e:
        logger.exception("Не удалось подключиться к PostgreSQL")
        hint = _db_connection_hint()
        raise RuntimeError(hint) from e

    # Выполняем миграции, если Alembic есть и миграции разрешены
    if alembic_present and settings.USE_MIGRATIONS:
        await run_migrations_if_needed()
    elif alembic_present:
        print("ℹ Alembic найден, но миграции отключены (USE_MIGRATIONS=False).")

    # Создаём суперюзера; при SALES_SEED_CSV_PATH — первичный импорт датасета (например ВКР)
    async with AsyncSessionLocal() as session:
        await create_superuser_if_not_exists(session)
        await run_sales_csv_seed_if_configured(session)
