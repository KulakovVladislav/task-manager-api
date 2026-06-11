import uuid
from datetime import timedelta, datetime, timezone

from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError
from passlib.context import CryptContext

from app.config import settings
from app.schemas import TokenData

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto",
    bcrypt__rounds=12
)
DUMMY_PASSWORD_HASH = "$2b$12$3dPBqBJA.hPt4sdd7BJ7k.fHvIAEFvD.I4bMnRKSSmC0iP.gkKJK2"
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/users/login")


def hash_password(password: str):
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str):
    return pwd_context.verify(plain_password, hashed_password)


def create_access_token(data: dict):
    jti = str(uuid.uuid4())
    to_encode = data.copy()
    to_encode.update({
        "exp": datetime.now(timezone.utc) + timedelta(minutes=settings.access_token_expire_minutes),
        "jti": jti
    })
    encoded_jwt = jwt.encode(to_encode, settings.secret_key, algorithm=settings.algorithm)
    return encoded_jwt


def decode_access_token(token: str):
    try:
        payload = jwt.decode(token, settings.secret_key, algorithms=[settings.algorithm])
        subject = payload.get("sub")
        jti = payload.get("jti")
        exp = payload.get("exp")
        if not subject or not jti or not exp:
            return None
        return TokenData(sub=subject, jti=jti, exp=exp)
    except JWTError:
        return None
