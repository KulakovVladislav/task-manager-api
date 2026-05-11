from fastapi import Depends
from sqlalchemy.orm import Session

from app.database.db import get_db
from app.security import oauth2_scheme
from app.services.user_service import get_current_user


def get_current_user_dependency(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):
    return get_current_user(token, db)
