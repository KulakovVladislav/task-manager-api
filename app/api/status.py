from fastapi import APIRouter, Depends

from app.config import settings
from app.database.models import User
from app.dependencies import get_current_user_dependency

router = APIRouter()


@router.get("/ping")
def ping():
    return {"status": "ok", "message": "pong"}


@router.get("/db-info")
def db_info(current_user: User = Depends(get_current_user_dependency)):
    """DB info endpoint - only accessible to authenticated users"""
    return {"db_host": settings.db_host,
            "db_port": settings.db_port
            }


@router.get("/info")
def info():
    return {"app_title": settings.app_title, "status": "running"}


@router.get("/")
def read_root():
    return {"message": "Hello Backend"}


@router.get("/hello")
def hello():
    return {"message": "hello Vlad"}


@router.get("/health")
def health_info():
    return {"status": "ok"}
