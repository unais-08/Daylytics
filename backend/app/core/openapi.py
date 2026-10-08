"""OpenAPI customization shared by the application factory."""

from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi


def configure_openapi(app: FastAPI) -> None:
    def custom_openapi():
        if app.openapi_schema:
            return app.openapi_schema
        schema = get_openapi(
            title=app.title,
            version=app.version,
            routes=app.routes,
            description="Local-first personal analytics API.",
        )
        schema.setdefault("components", {}).setdefault("schemas", {})[
            "ErrorResponse"
        ] = {
            "title": "ErrorResponse",
            "type": "object",
            "required": ["error"],
            "properties": {
                "error": {
                    "type": "object",
                    "required": ["code", "message", "request_id"],
                    "properties": {
                        "code": {"type": "string"},
                        "message": {"type": "string"},
                        "details": {"type": "object"},
                        "request_id": {"type": "string", "format": "uuid"},
                    },
                }
            },
        }
        error_ref = {"$ref": "#/components/schemas/ErrorResponse"}
        for path in schema.get("paths", {}).values():
            for operation in path.values():
                if isinstance(operation, dict) and "responses" in operation:
                    for status in ("400", "404", "409", "422", "500"):
                        operation["responses"].setdefault(
                            status,
                            {
                                "description": "Standard error response",
                                "content": {"application/json": {"schema": error_ref}},
                            },
                        )
        app.openapi_schema = schema
        return schema

    app.openapi = custom_openapi
