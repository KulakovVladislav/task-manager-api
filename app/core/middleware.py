import logging
import time
import traceback

from fastapi import FastAPI, Request, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("profiler")


class ProfilerAndExceptionMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        start_time = time.perf_counter()

        try:
            response: Response = await call_next(request)

        except Exception as exc:
            stack_trace = traceback.format_exc()
            logger.error(f"[UNEXPECTED ERROR] {exc}\n{stack_trace}")

            response = JSONResponse(
                status_code=500,
                content={"detail": "Internal Server Error"}
            )

        process_time = (time.perf_counter() - start_time) * 1000
        latency_str = f"{process_time:.2f}ms"

        response.headers["X-Response-Time"] = latency_str

        logger.info(
            f"[PROFILER] Method: {request.method} | "
            f"Path: {request.url.path} | "
            f"Status: {response.status_code} | "
            f"Latency: {latency_str}"
        )

        return response


def register_middlewares(app: FastAPI) -> None:
    app.add_middleware(ProfilerAndExceptionMiddleware)
