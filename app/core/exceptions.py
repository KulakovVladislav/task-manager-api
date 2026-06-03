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


class UsernameAlreadyTakenError(DomainException):
    pass


class EmailAlreadyRegisteredError(DomainException):
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
        status_code=404,
        content={"detail": detail}
    )


async def authentication_failed_error_handler(request: Request, exc: AuthenticationFailedError):
    detail = str(exc) or "invalid token"

    return JSONResponse(
        status_code=401,
        content={"detail": detail}
    )


async def username_taken_failed_error_handler(request: Request, exc: UsernameAlreadyTakenError):
    detail = str(exc) or "Username already taken"

    return JSONResponse(
        status_code=400,
        content={"detail": detail}
    )


async def email_registered_failed_error_handler(request: Request, exc: EmailAlreadyRegisteredError):
    detail = str(exc) or "Email already registered"

    return JSONResponse(
        status_code=400,
        content={"detail": detail}
    )


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(UserNotFoundError, user_not_found_exception_handler)
    app.add_exception_handler(TaskNotFoundError, task_not_found_exception_handler)
    app.add_exception_handler(AuthenticationFailedError, authentication_failed_error_handler)
    app.add_exception_handler(UsernameAlreadyTakenError, username_taken_failed_error_handler)
    app.add_exception_handler(EmailAlreadyRegisteredError, email_registered_failed_error_handler)

