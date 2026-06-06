from datetime import timedelta, datetime, timezone

from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings

BCRYPT_ROUNDS = 12
BCRYPT_MAX_PASSWORD_LENGTH = 72

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)
DUMMY_PASSWORD_HASH = "$2b$12$3dPBqBJA.hPt4sdd7BJ7k.fHvIAEFvD.I4bMnRKSSmC0iP.gkKJK2"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def hash_password(password: str):
    """Hash password with truncation to bcrypt's 72-byte limit"""
    # Truncate password to 72 bytes to comply with bcrypt limitation
    truncated_password = password[:BCRYPT_MAX_PASSWORD_LENGTH]
    return pwd_context.hash(truncated_password)


def verify_password(plain_password: str, hashed_password: str):
    """Verify password with truncation to bcrypt's 72-byte limit"""
    # Truncate password to 72 bytes to comply with bcrypt limitation
    truncated_password = plain_password[:BCRYPT_MAX_PASSWORD_LENGTH]
    return pwd_context.verify(truncated_password, hashed_password)


def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
    except JWTError:
        return None
    subject = payload.get("sub")
    if not subject:
        return None
    return subject
