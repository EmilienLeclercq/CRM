from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_db, validate_refresh_token
from app.models import RefreshToken, User
from app.schemas.auth import LoginRequest, RefreshRequest, TokenResponse
from app.schemas.user import UserOut
from app.services.auth import (
    create_access_token,
    create_refresh_token,
    hash_password,
    refresh_expiration,
    verify_password,
)

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/login", response_model=TokenResponse)
def login(payload: LoginRequest, db: Session = Depends(get_db)) -> TokenResponse:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials")

    access_token = create_access_token(str(user.id))
    refresh_token_value = create_refresh_token()
    refresh = RefreshToken(
        token=refresh_token_value,
        user_id=user.id,
        expires_at=refresh_expiration(),
    )
    db.add(refresh)
    db.commit()
    return TokenResponse(access_token=access_token, refresh_token=refresh_token_value)


@router.post("/refresh", response_model=TokenResponse)
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)) -> TokenResponse:
    refresh_token = validate_refresh_token(db, payload.refresh_token)
    db.delete(refresh_token)
    access_token = create_access_token(str(refresh_token.user_id))
    new_refresh_value = create_refresh_token()
    db.add(
        RefreshToken(
            token=new_refresh_value,
            user_id=refresh_token.user_id,
            expires_at=refresh_expiration(),
        )
    )
    db.commit()
    return TokenResponse(access_token=access_token, refresh_token=new_refresh_value)


@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)) -> UserOut:
    return current_user


def ensure_password(user: User, password: str) -> None:
    if not user.hashed_password:
        user.hashed_password = hash_password(password)
