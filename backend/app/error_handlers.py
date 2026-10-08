from __future__ import annotations

import logging
from typing import Any

from fastapi import Request
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from sqlalchemy.exc import IntegrityError, OperationalError
from starlette.exceptions import HTTPException as StarletteHTTPException

from app.exceptions import AppError
from app.messages import MESSAGES

logger = logging.getLogger("personal_analytics")


def request_id(request: Request) -> str:
    return getattr(request.state, "request_id", "00000000-0000-0000-0000-000000000000")


def error_response(
    request: Request,
    code: str,
    message: str,
    status: int,
    details: dict[str, Any] | None = None,
) -> JSONResponse:
    rid = request_id(request)
    body = {"error": {"code": code, "message": message, "request_id": rid}}
    if details:
        body["error"]["details"] = details
    response = JSONResponse(status_code=status, content=body)
    response.headers["X-Request-ID"] = rid
    return response


def _friendly_validation(exc: RequestValidationError) -> list[dict[str, str]]:
    fields = []
    for error in exc.errors():
        location = error.get("loc", ())
        field = str(location[-1]) if location else "request"
        error_type = error.get("type", "")
        context = error.get("ctx", {})
        if error_type == "missing":
            message = "This field is required."
        elif error_type in {"greater_than_equal", "greater_than"}:
            message = (
                f"This value must be at least {context.get('ge', context.get('gt'))}."
            )
        elif error_type in {"less_than_equal", "less_than"}:
            message = (
                f"This value must be at most {context.get('le', context.get('lt'))}."
            )
        elif error_type == "enum":
            allowed = ", ".join(
                str(value) for value in context.get("expected", "").split(", ")
            )
            message = f"Choose one of the allowed values: {allowed}."
        elif error_type in {"datetime_parsing", "date_from_datetime_parsing"}:
            message = "Use a valid ISO-8601 date or datetime."
        elif error_type == "int_parsing":
            message = "Enter a whole number."
        else:
            message = "Check this value and try again."
        fields.append({"field": field, "message": message})
    return fields


async def app_error_handler(request: Request, exc: AppError):
    logger.warning(
        "client_error code=%s path=%s method=%s request_id=%s",
        exc.code,
        request.url.path,
        request.method,
        request_id(request),
    )
    return error_response(request, exc.code, exc.message, exc.status_code, exc.details)


async def validation_error_handler(request: Request, exc: RequestValidationError):
    fields = _friendly_validation(exc)
    logger.info(
        "validation_error path=%s method=%s request_id=%s",
        request.url.path,
        request.method,
        request_id(request),
    )
    return error_response(
        request,
        "VALIDATION_ERROR",
        MESSAGES["VALIDATION_ERROR"],
        422,
        {"fields": fields},
    )


async def http_error_handler(request: Request, exc: StarletteHTTPException):
    if exc.status_code == 404:
        code, message = "ROUTE_NOT_FOUND", MESSAGES["ROUTE_NOT_FOUND"]
    elif exc.status_code == 405:
        code, message = "METHOD_NOT_ALLOWED", MESSAGES["METHOD_NOT_ALLOWED"]
    else:
        code, message = "HTTP_ERROR", "The request could not be completed."
    logger.info(
        "http_error status=%s path=%s method=%s request_id=%s",
        exc.status_code,
        request.url.path,
        request.method,
        request_id(request),
    )
    return error_response(request, code, message, exc.status_code)


async def integrity_error_handler(request: Request, exc: IntegrityError):
    logger.warning(
        "integrity_error path=%s method=%s request_id=%s",
        request.url.path,
        request.method,
        request_id(request),
    )
    message = (
        MESSAGES["DUPLICATE_ENTRY"]
        if "UNIQUE" in str(exc.orig).upper()
        else MESSAGES["CONSTRAINT_VIOLATION"]
    )
    code = (
        "DUPLICATE_ENTRY"
        if message == MESSAGES["DUPLICATE_ENTRY"]
        else "CONSTRAINT_VIOLATION"
    )
    return error_response(request, code, message, 409)


async def operational_error_handler(request: Request, exc: OperationalError):
    logger.exception(
        "database_unavailable path=%s method=%s request_id=%s",
        request.url.path,
        request.method,
        request_id(request),
    )
    return error_response(
        request, "DATABASE_UNAVAILABLE", MESSAGES["DATABASE_UNAVAILABLE"], 503
    )


async def unhandled_error_handler(request: Request, exc: Exception):
    logger.exception(
        "internal_error path=%s method=%s request_id=%s",
        request.url.path,
        request.method,
        request_id(request),
    )
    return error_response(request, "INTERNAL_ERROR", MESSAGES["INTERNAL_ERROR"], 500)
