from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.database.models import User
from app.schemas import UserCreate
from app.security import decode_access_token
from app.security import hash_password, verify_password


def get_user_by_email(email: str, db: Session):
    db_user = db.query(User).filter(User.email == email).first()
    return db_user


def create_user(user: UserCreate, db: Session):
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


def authenticate_user(email: str, password: str, db: Session):
    user = get_user_by_email(email, db)
    if not user:
        return None
    is_password_valid = verify_password(password, user.hashed_password)
    if not is_password_valid:
        return None
    return user


def get_current_user(token: str, db: Session):
    email = decode_access_token(token)
    if not email:
        raise HTTPException(status_code=401, detail="Invalid token")

    user = get_user_by_email(email, db)
    if not user:
        raise HTTPException(status_code=401, detail="Invalid token")
    return user
