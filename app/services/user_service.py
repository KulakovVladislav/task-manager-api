from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationFailedError
from app.database.models import User
from app.schemas import UserCreate, TokenData
from app.security import decode_access_token, DUMMY_PASSWORD_HASH
from app.security import hash_password, verify_password


def get_user_by_email(email: str, db: Session):
    db_user = db.query(User).filter(User.email == email).first()
    return db_user


def get_user_by_username(username: str, db: Session):
    db_user = db.query(User).filter(User.username == username).first()
    return db_user


def create_user(user: UserCreate, db: Session):
    db_user = User(
        username=user.username,
        email=user.email,
        hashed_password=hash_password(user.password)
    )
    db.add(db_user)
    db.flush()
    return db_user


def authenticate_user(email: str, password: str, db: Session):
    db_user = get_user_by_email(email, db)
    if db_user is not None:
        password_hash_to_verify = db_user.hashed_password
    else:
        password_hash_to_verify = DUMMY_PASSWORD_HASH
    is_password_valid = verify_password(password, password_hash_to_verify)
    if db_user is None:
        raise AuthenticationFailedError("Incorrect email or password")
    if not is_password_valid:
        raise AuthenticationFailedError("Incorrect email or password")
    if not db_user.is_active:
        raise AuthenticationFailedError("User account is inactive")
    return db_user


def get_current_user(token_data: TokenData, db: Session, redis_client):
    if token_data is None:
        raise AuthenticationFailedError("invalid token")
    jti = token_data.jti
    email = token_data.sub
    key = f"blacklist:jti:{token_data.jti}"
    if redis_client.exists(key):
        raise AuthenticationFailedError("Token has been revoked")
    if not email:
        raise AuthenticationFailedError("invalid token")
    user = get_user_by_email(email, db)
    if not user:
        raise AuthenticationFailedError("user not found")
    if not user.is_active:
        raise AuthenticationFailedError("User account is inactive")
    return user
