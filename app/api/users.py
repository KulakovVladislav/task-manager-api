from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.orm import Session

from app.config import settings
from app.database.db import get_db
from app.database.models import User
from app.dependencies import get_current_user_dependency
from app.schemas import Token
from app.schemas import UserCreate, UserResponse, UserLogin
from app.security import create_access_token
from app.services.user_service import get_user_by_email, create_user, authenticate_user

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register_user(item: UserCreate, db: Session = Depends(get_db)):
    db_user = get_user_by_email(item.email, db)
    if db_user:
        raise HTTPException(status_code=400, detail="Email already registered")
    db_user = create_user(item, db)
    return db_user


@router.post("/login", response_model=Token)
def login_user(item: UserLogin, db: Session = Depends(get_db)):
    db_user = authenticate_user(item.email, item.password, db)
    if not db_user:
        raise HTTPException(status_code=401, detail="Incorrect email or password")
    access_token = create_access_token(data={"sub": db_user.email})
    return {"access_token": access_token, "token_type": "bearer", "expires_in": settings.access_token_expire_minutes}


@router.get("/me", response_model=UserResponse)
def get_me(current_user: User = Depends(get_current_user_dependency)):
    return current_user
