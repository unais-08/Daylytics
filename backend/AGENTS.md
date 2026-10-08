# Backend agent guide

## Purpose

This is a local-first FastAPI analytics backend. It records work sessions,
distractions, sleep, prayers, and career output, then computes pandas-based
analytics without external services.

## Folder map

- `app/main.py`: `create_app()` and ASGI entry point.
- `app/core/`: shared infrastructure; never imports feature modules.
- `app/api/`: dependency providers and the single router composition point.
- `app/modules/<feature>/`: models, schemas, services, optional queries, and
  thin HTTP routers.
- `app/analytics/`: pure pandas analysis functions and frame construction.
- `app/db/base.py`: imports every model for Alembic metadata registration.
- `tests/`: API, module, analytics, and architecture tests.

## Dependency contract

Core cannot import `api`, `modules`, or `analytics`. Pure analytics cannot
import FastAPI, SQLAlchemy, or modules. Routers parse input and call their own
services; services own business rules and may call other services, never
routers. Only `app/api/router.py` includes module routers.

## Commands

```powershell
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn app.main:app --reload
pytest -q
ruff check app alembic tests
alembic upgrade head
python scripts/seed.py
python scripts/check_openapi.py
```

## Add a module

1. Create `app/modules/<feature>/` with a package docstring.
2. Add `models.py` and register the model in `app/db/base.py`.
3. Add Pydantic types in `schemas.py`.
4. Put rules and orchestration in `service.py`; move crowded selects to
   `queries.py`.
5. Keep `router.py` to parse -> service -> return and include it in
   `app/api/router.py`.
6. Add mirrored tests, update docs, and run the complete command set.

## Add an analysis

1. Add one pure function in the focused `app/analytics/*.py` module.
2. Accept DataFrames or plain records and return plain dictionaries.
3. Keep database loading and filter validation in
   `app/modules/analytics/service.py`.
4. Add the analysis name to the service allow-list and dispatcher.
5. Add analytics tests, then run pytest, Ruff, and the OpenAPI check.

## Do not

- Change endpoint paths, schemas, error codes, database schema, or behavior.
- Put SQL, business rules, or broad exception handling in routers.
- Import FastAPI or SQLAlchemy into pure analytics.
- Add repositories, generic helpers, dependency frameworks, or duplicate
  compatibility implementations.
- Skip tests, weaken architecture checks, or commit generated secrets.
