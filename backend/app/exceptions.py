from typing import Any

from app.messages import MESSAGES


class AppError(Exception):
    def __init__(
        self,
        code: str,
        message: str | None = None,
        status_code: int = 400,
        details: dict[str, Any] | None = None,
    ):
        self.code = code
        self.message = message or MESSAGES.get(
            code, "The request could not be completed."
        )
        self.status_code = status_code
        self.details = details
        super().__init__(self.message)


class NotFoundError(AppError):
    def __init__(self, code: str, details: dict[str, Any] | None = None):
        super().__init__(code, status_code=404, details=details)


class ConflictError(AppError):
    def __init__(self, code: str, details: dict[str, Any] | None = None):
        super().__init__(code, status_code=409, details=details)


class BusinessRuleError(AppError):
    def __init__(
        self,
        code: str,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(code, message=message, status_code=422, details=details)


class InvalidParameterError(AppError):
    def __init__(
        self,
        code: str,
        message: str | None = None,
        details: dict[str, Any] | None = None,
    ):
        super().__init__(code, message=message, status_code=400, details=details)


class DangerousActionError(AppError):
    def __init__(self, code: str, details: dict[str, Any] | None = None):
        super().__init__(code, status_code=400, details=details)
