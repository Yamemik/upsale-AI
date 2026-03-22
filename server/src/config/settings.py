from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Upsale-AI"
    DEBUG: bool = True

    # database
    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    USE_MIGRATIONS: bool = False

    # первичная загрузка sales из CSV (Kaggle sales_train / ВКР); пусто = отключено
    SALES_SEED_CSV_PATH: str | None = None
    SALES_SEED_ONLY_IF_EMPTY: bool = True
    # auto — по заголовкам (sales_train Kaggle распознаётся автоматически); kaggle | legacy
    SALES_IMPORT_DEFAULT_FORMAT: str = "auto"

    # Прогноз: lightgbm | catboost (catboost требует pip install catboost)
    FORECAST_MODEL_BACKEND: str = "lightgbm"

    # superuser
    SUPERUSER_NAME: str = "admin"
    SUPERUSER_EMAIL: str 
    SUPERUSER_PASSWORD: str | None = None

    # jwt
    JWT_SECRET_KEY: str
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
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
