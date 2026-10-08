# Decisions

- Use a single FastAPI application for the MVP; routers can be split as the API grows.
- Use SQLite with SQLAlchemy 2 typed models and UTC-aware timestamps.
- Derive durations and deep-work defaults rather than storing redundant values.
- Keep the initial implementation dependency-light and preserve a portable SQLAlchemy model shape.
