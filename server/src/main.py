import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.utils import get_openapi

from src.config.settings import settings
from src.api.v1.router import api_router
from src.db.init_db import init_db
from src.db.session import AsyncSessionLocal, engine
from src.features.integration_1s.api.sync_public_routes import Integration1SPublicRoutes

logger = logging.getLogger(__name__)


async def _1c_auto_sync_loop() -> None:
    """Периодическое дополнение sales из 1С (см. INTEGRATION_1C_AUTO_SYNC_*)."""
    interval = max(1, settings.INTEGRATION_1C_AUTO_SYNC_INTERVAL_HOURS) * 3600
    while True:
        try:
            from src.features.integration_1s.services.onec_sales_import_service import (
                import_onec_sales_from_odata,
            )

            async with AsyncSessionLocal() as session:
                result = await import_onec_sales_from_odata(session, settings)
                logger.info(
                    "1C auto-sync: imported=%s date_from=%s",
                    result.get("imported"),
                    result.get("date_from"),
                )
        except Exception:
            logger.exception("1C auto-sync failed")
        await asyncio.sleep(interval)


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()

    task: asyncio.Task | None = None
    if (
        settings.INTEGRATION_1C_AUTO_SYNC_ENABLED
        and settings.INTEGRATION_1C_BASE_URL
        and settings.INTEGRATION_1C_USERNAME
    ):
        task = asyncio.create_task(_1c_auto_sync_loop())

    yield

    if task:
        task.cancel()
        try:
            await task
        except asyncio.CancelledError:
            pass

    await engine.dispose()


app = FastAPI(
    debug=settings.DEBUG,
    docs_url="/api/docs",
    openapi_url="/api/openapi.json",
    title=f"{settings.APP_NAME} API docs",
    lifespan=lifespan
)
    
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # лучше ограничить доменами в продакшене
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

def custom_openapi():
    if app.openapi_schema:
        return app.openapi_schema
    openapi_schema = get_openapi(
        title=settings.APP_NAME,
        version="1.0.0",
        description="API с JWT авторизацией",
        routes=app.routes,
    )
    openapi_schema["components"]["securitySchemes"] = {
        "BearerAuth": {
            "type": "http",
            "scheme": "bearer",
            "bearerFormat": "JWT",
        }
    }
    for path in openapi_schema["paths"].values():
        for operation in path.values():
            operation.setdefault("security", []).append({"BearerAuth": []})
    app.openapi_schema = openapi_schema
    return app.openapi_schema

app.openapi = custom_openapi

app.include_router(api_router)
app.include_router(Integration1SPublicRoutes().router, prefix="/api")
