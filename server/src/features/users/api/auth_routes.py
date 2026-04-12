from fastapi import APIRouter, Depends
from fastapi.security import OAuth2PasswordRequestForm

from ..schemas.user_schema import Token
from ..dependencies import get_auth_service
from ..services.auth_service import AuthService


class AuthRoutes:
    def __init__(self):
        self.router = APIRouter(prefix="/auth", tags=["Auth"])
        self._register_routes()

    def _register_routes(self):
        @self.router.post("/login", response_model=Token)
        async def login(
            form_data: OAuth2PasswordRequestForm = Depends(),
            auth_service: AuthService = Depends(get_auth_service),
        ):
            user = await auth_service.authenticate_user(form_data.username, form_data.password)
            token = auth_service.create_access_token(subject=str(user.id))
            return Token(access_token=token, token_type="bearer")
