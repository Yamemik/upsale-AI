from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    APP_NAME: str = "FastAPI Upsale-AI"
    DEBUG: bool = True

    # database
    DATABASE_URL: str
    DATABASE_URL_SYNC: str
    USE_MIGRATIONS: bool = False

    # первичная загрузка sales из CSV (ВКР / сиды); пусто = отключено
    SALES_SEED_CSV_PATH: str | None = None
    SALES_SEED_ONLY_IF_EMPTY: bool = True

    # superuser
    SUPERUSER_NAME: str = "admin"
    SUPERUSER_EMAIL: str 
    SUPERUSER_PASSWORD: str | None = None

    # jwt
    JWT_SECRET_KEY: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 15
    REFRESH_TOKEN_EXPIRE_DAYS: int = 7

    model_config = SettingsConfigDict(
        env_file=".env",
        extra="ignore",
    )


settings = Settings()
