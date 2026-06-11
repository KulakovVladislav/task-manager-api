from fastapi import Depends
from sqlalchemy.orm import Session

from app.core.exceptions import AuthenticationFailedError
from app.core.redis import get_redis_client
from app.database.db import get_db
from app.schemas import TokenData
from app.security import oauth2_scheme, decode_access_token
from app.services.user_service import get_current_user


def get_token_data_dependency(token: str = Depends(oauth2_scheme)):
    token_data = decode_access_token(token)
    if token_data is None:
        raise AuthenticationFailedError("invalid token")
    return token_data


def get_current_user_dependency(token_data: TokenData = Depends(get_token_data_dependency),
                                db: Session = Depends(get_db), redis=Depends(get_redis_client)):
    return get_current_user(token_data, db, redis)
