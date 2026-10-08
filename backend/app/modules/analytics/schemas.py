"""Schemas for analytics request parameters and dynamic analysis responses."""

from datetime import date

from pydantic import BaseModel


class AnalyticsRange(BaseModel):
    start_date: date | None
    end_date: date | None
    name: str
