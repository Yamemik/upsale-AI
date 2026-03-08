from fastapi import HTTPException
from src.features.users.models.user_model import User as AuthUser


def check_admin(user: AuthUser):
    if not getattr(user, "is_admin", False):
        raise HTTPException(status_code=403, detail="Admin privileges required")
