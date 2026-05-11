from fastapi import FastAPI

from app.api.status import router as status_router
from app.api.tasks import router as task_router
from app.api.users import router as user_router
from app.config import settings

app = FastAPI(title=settings.app_title)

app.include_router(task_router, tags=["Tasks"])
app.include_router(status_router, prefix="/system", tags=["System"])
app.include_router(user_router, prefix="/users", tags=["Users"])
