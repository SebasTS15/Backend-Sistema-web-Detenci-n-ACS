from datetime import timedelta

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from app.core.config import get_settings
from app.core.security import create_access_token

router = APIRouter(prefix="/api/v1/auth", tags=["auth"])


class AuthRequest(BaseModel):
    username: str = Field(..., min_length=1)
    password: str = Field(..., min_length=1)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"


@router.post("/token", response_model=TokenResponse)
def login_for_access_token(credentials: AuthRequest) -> TokenResponse:
    settings = get_settings()

    if (
        credentials.username != settings.auth_username
        or credentials.password != settings.auth_password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Credenciales inválidas.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    access_token_expires = timedelta(minutes=settings.jwt_access_token_expires_minutes)
    access_token = create_access_token(
        subject=credentials.username,
        expires_delta=access_token_expires,
    )
    return TokenResponse(access_token=access_token)
