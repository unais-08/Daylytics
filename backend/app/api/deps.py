"""Shared FastAPI dependencies exposed to feature routers."""

from app.core.database import get_db

__all__ = ["get_db"]
