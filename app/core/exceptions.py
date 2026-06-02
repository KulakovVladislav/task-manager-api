from fastapi import Request, FastAPI
from fastapi.responses import JSONResponse


class DomainException(Exception):
    pass


class UserNotFoundError(DomainException):
    pass


class TaskNotFoundError(DomainException):
    pass


class AuthenticationFailedError(DomainException):
    pass


async def task_not_found_exception_handler(request: Request, exc: TaskNotFoundError):
    detail = str(exc) or "task not found"

    return JSONResponse(
        status_code=404,
        content={"detail": detail}
    )


async def user_not_found_exception_handler(request: Request, exc: UserNotFoundError):
    detail = str(exc) or "user not found"

    return JSONResponse(
        status_code=401,
        content={"detail": detail}
    )


async def authentication_failed_error_handler(request: Request, exc: AuthenticationFailedError):
    detail = str(exc) or "invalid token"

    return JSONResponse(
        status_code=404,
        content={"detail": detail}
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UserNotFoundError, user_not_found_exception_handler)
    app.add_exception_handler(TaskNotFoundError, task_not_found_exception_handler)
    app.add_exception_handler(AuthenticationFailedError, authentication_failed_error_handler)
