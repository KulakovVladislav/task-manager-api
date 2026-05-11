from fastapi import APIRouter

from app.config import settings

router = APIRouter()


@router.get("/ping")
def ping():
    return {"status": "ok", "message": "pong"}


@router.get("/db-info")
def db_info():
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
