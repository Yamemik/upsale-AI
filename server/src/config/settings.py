from pathlib import Path

from pydantic import Field
from pydantic_settings import BaseSettings, SettingsConfigDict

# Корень пакета server/ — .env ищется здесь, независимо от cwd при запуске uvicorn
_SERVER_ROOT = Path(__file__).resolve().parents[2]


class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Upsale-AI"
    DEBUG: bool = True

    # database (в продакшене задайте через .env или переменные окружения)
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://postgres:postgres@127.0.0.1:5432/upsale-db",
        description="Async SQLAlchemy URL",
    )
    DATABASE_URL_SYNC: str = Field(
        default="postgresql://postgres:postgres@127.0.0.1:5432/upsale-db",
        description="Sync URL (Alembic и т.п.)",
    )
    USE_MIGRATIONS: bool = False

    # asyncpg: таймаут подключения (сек.); при WinError 10054 на локальном Postgres попробуйте DATABASE_SSL_DISABLE=true
    DATABASE_CONNECT_TIMEOUT: int = Field(default=30, ge=5, le=120)
    DATABASE_SSL_DISABLE: bool = Field(
        default=False,
        description="True — ssl=False в asyncpg (часто нужно для локального Postgres на Windows)",
    )

    # первичная загрузка sales из CSV (Kaggle sales_train / ВКР); пусто = отключено
    SALES_SEED_CSV_PATH: str | None = None
    SALES_SEED_ONLY_IF_EMPTY: bool = True
    # auto — по заголовкам (sales_train Kaggle распознаётся автоматически); kaggle | legacy
    SALES_IMPORT_DEFAULT_FORMAT: str = "auto"

    # Прогноз: lightgbm | catboost (catboost требует pip install catboost)
    FORECAST_MODEL_BACKEND: str = "lightgbm"

    # superuser
    SUPERUSER_NAME: str = "admin"
    SUPERUSER_EMAIL: str = Field(default="admin@localhost")
    SUPERUSER_PASSWORD: str | None = None

    # jwt (в продакшене обязательно переопределите JWT_SECRET_KEY)
    JWT_SECRET_KEY: str = Field(
        default="dev-only-change-me-use-long-random-string-in-production",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    # 1C OData (опционально; для /integration/1c/...)
    INTEGRATION_1C_BASE_URL: str | None = None
    INTEGRATION_1C_USERNAME: str | None = None
    INTEGRATION_1C_PASSWORD: str | None = None
    # Документ реализации и табличная часть (имена сущностей OData в вашей базе)
    INTEGRATION_1C_ODATA_DOCUMENT_PATH: str = "Document_РеализацияТоваровУслуг"
    INTEGRATION_1C_ODATA_EXPAND_LINE_ITEMS: str = "Товары"
    # Справочники для имён магазина/номенклатуры (при необходимости поменять под конфигурацию)
    INTEGRATION_1C_ODATA_SHOP_CATALOG: str = "Catalog_Склады"
    INTEGRATION_1C_ODATA_ITEM_CATALOG: str = "Catalog_Номенклатура"
    # Опционально: URL HTTP-сервиса 1С для приёма заказов (см. OneCPushService)
    INTEGRATION_1C_PUSH_ORDERS_URL: str | None = None
    # Поле даты документа в OData для $filter (при необходимости замените на Дата)
    INTEGRATION_1C_ODATA_DOCUMENT_DATE_FIELD: str = "Date"
    # Инкрементальная синхронизация в БД после первичного CSV
    INTEGRATION_1C_SYNC_LOOKBACK_DAYS: int = 7
    INTEGRATION_1C_SYNC_FROM_MAX_SALE_DATE: bool = True
    INTEGRATION_1C_SYNC_OVERLAP_DAYS: int = 1
    INTEGRATION_1C_AUTO_SYNC_ENABLED: bool = False
    INTEGRATION_1C_AUTO_SYNC_INTERVAL_HOURS: int = 168

    model_config = SettingsConfigDict(
        env_file=(
            _SERVER_ROOT / ".env",
            _SERVER_ROOT / ".env.local",
        ),
        env_file_encoding="utf-8",
        extra="ignore",
    )


settings = Settings()
