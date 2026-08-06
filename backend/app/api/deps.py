from collections.abc import Generator

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.ai_provider import AIProvider, get_provider
from app.core.security import decode_access_token
from app.models.database import get_db
from app.models.models import User

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login", auto_error=False)


def get_current_user(
    token: str | None = Depends(oauth2_scheme),
    db: Session = Depends(get_db),
) -> User:
    credentials_error = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    if not token:
        raise credentials_error
    user_id = decode_access_token(token)
    if not user_id:
        raise credentials_error
    user = db.get(User, user_id)
    if not user:
        raise credentials_error
    return user


def get_ai_provider() -> AIProvider:
    return get_provider()
