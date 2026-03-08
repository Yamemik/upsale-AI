import hashlib

from sqlalchemy.sql import func

from ..models.apikey_model import ApiKey
from ..repositories.apikey_repository import ApiKeyRepository


class ApiKeyService:
    def __init__(self, repo: ApiKeyRepository):
        self.repo = repo

    async def validate_api_key(self, raw_key: str) -> ApiKey | None:
        key_hash = hashlib.sha256(raw_key.encode()).hexdigest()
        api_key = await self.repo.get_by_hash(key_hash)

        if not api_key or not api_key.is_active:
            return None

        api_key.last_used_at = func.now()
        await self.repo.db.commit()

        return api_key

