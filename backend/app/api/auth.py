from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.security import create_access_token, hash_password, verify_password
from app.models.database import get_db
from app.models.models import User
from app.schemas.schemas import Token, UserCreate, UserLogin, UserOut

router = APIRouter(prefix="/api/auth", tags=["auth"])

DEMO_EMAIL = "demo@creatoros.ai"


@router.post("/register", response_model=UserOut, status_code=status.HTTP_201_CREATED)
def register(payload: UserCreate, db: Session = Depends(get_db)) -> User:
    existing = db.query(User).filter(User.email == payload.email).first()
    if existing:
        raise HTTPException(status_code=400, detail="Email already registered")
    user = User(
        email=payload.email,
        hashed_password=hash_password(payload.password),
        display_name=payload.display_name,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    return user


@router.post("/login", response_model=Token)
def login(payload: UserLogin, db: Session = Depends(get_db)) -> Token:
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    return Token(access_token=create_access_token(user.id))


@router.post("/demo-login", response_model=Token)
def demo_login(db: Session = Depends(get_db)) -> Token:
    """One-click login for judges/demo: creates (or reuses) a fixed demo
    account so nobody needs real credentials to try the product."""
    user = db.query(User).filter(User.email == DEMO_EMAIL).first()
    if not user:
        user = User(
            email=DEMO_EMAIL,
            hashed_password=hash_password("not-a-real-password"),
            display_name="Demo Creator",
        )
        db.add(user)
        db.commit()
        db.refresh(user)
    return Token(access_token=create_access_token(user.id))
