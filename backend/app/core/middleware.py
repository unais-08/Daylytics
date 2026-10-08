import logging
from uuid import UUID, uuid4

from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("personal_analytics")


class RequestIDMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        incoming = request.headers.get("X-Request-ID")
        try:
            request_id = str(UUID(incoming)) if incoming else str(uuid4())
        except ValueError:
            request_id = str(uuid4())
        request.state.request_id = request_id
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        logger.info(
            "request method=%s path=%s status=%s request_id=%s",
            request.method,
            request.url.path,
            response.status_code,
            request_id,
        )
        return response
