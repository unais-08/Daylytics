"""Application factory and ASGI application entry point."""

from fastapi import FastAPI
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.exc import IntegrityError, OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.api.router import router as api_router
from app.core.error_handlers import (
    app_error_handler,
    http_error_handler,
    integrity_error_handler,
    operational_error_handler,
    unhandled_error_handler,
    validation_error_handler,
)
from app.core.exceptions import AppError
from app.core.logging import configure_logging
from app.core.middleware import RequestIDMiddleware
from app.core.openapi import configure_openapi


def create_app() -> FastAPI:
    configure_logging()
    application = FastAPI(title="Personal Analytics API", version="0.1.0")
    application.add_middleware(RequestIDMiddleware)
    application.add_middleware(
        CORSMiddleware,
        allow_origins=["http://localhost:5173", "http://127.0.0.1:5173"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    application.add_exception_handler(Exception, unhandled_error_handler)
    application.add_exception_handler(AppError, app_error_handler)
    application.add_exception_handler(RequestValidationError, validation_error_handler)
    application.add_exception_handler(StarletteHTTPException, http_error_handler)
    application.add_exception_handler(IntegrityError, integrity_error_handler)
    application.add_exception_handler(OperationalError, operational_error_handler)
    application.include_router(api_router)
    configure_openapi(application)
    return application


app = create_app()
