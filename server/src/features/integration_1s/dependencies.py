from fastapi import Depends, Header, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession

from src.db.session import get_db
from .models.apikey_model import ApiKey
from .repositories.apikey_repository import ApiKeyRepository
from .services.apikey_service import ApiKeyService


def get_api_key_repository(
    db: AsyncSession = Depends(get_db),
) -> ApiKeyRepository:
    return ApiKeyRepository(db)


def get_api_key_service(
    repo: ApiKeyRepository = Depends(get_api_key_repository),
) -> ApiKeyService:
    return ApiKeyService(repo)


async def get_api_key(
    x_api_key: str = Header(None, alias="X-API-KEY"),
    service: ApiKeyService = Depends(get_api_key_service),
) -> ApiKey:
    if not x_api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="X-API-KEY header is missing",
        )

    api_key = await service.validate_api_key(x_api_key)

    if not api_key:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or inactive API key",
        )

    return api_key
