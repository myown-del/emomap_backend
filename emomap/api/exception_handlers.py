import logging
import traceback

from fastapi import FastAPI, HTTPException, Request
from fastapi.exception_handlers import http_exception_handler
from fastapi.responses import JSONResponse
from starlette import status


logger = logging.getLogger("uvicorn.error")


async def unhandled_exception_handler(request: Request, exc: Exception) -> JSONResponse:
    logger.error(
        "Unhandled exception on %s %s",
        request.method,
        request.url.path,
        exc_info=(type(exc), exc, exc.__traceback__),
    )
    return JSONResponse(
        status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
        content={
            "detail": "Unhandled exception",
            "exception_type": exc.__class__.__name__,
            "error": str(exc),
            "path": request.url.path,
            "traceback": "".join(
                traceback.format_exception(type(exc), exc, exc.__traceback__)
            ),
        },
    )


async def http_exception_with_logging(request: Request, exc: HTTPException) -> JSONResponse:
    if exc.status_code >= status.HTTP_500_INTERNAL_SERVER_ERROR:
        logger.error(
            "HTTPException %s on %s %s: %s",
            exc.status_code,
            request.method,
            request.url.path,
            exc.detail,
            exc_info=(type(exc), exc, exc.__traceback__),
        )
    return await http_exception_handler(request, exc)


def register_exception_handlers(app: FastAPI) -> None:
    app.add_exception_handler(HTTPException, http_exception_with_logging)
    app.add_exception_handler(Exception, unhandled_exception_handler)
