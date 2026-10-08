"""Top-level HTTP router for cross-feature and feature endpoints."""

from fastapi import APIRouter

router = APIRouter()


@router.get("/")
def root():
    return {"message": "Productivity API is running"}


@router.get("/health")
def health():
    return {"status": "ok"}
