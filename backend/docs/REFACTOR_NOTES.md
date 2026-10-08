# Modularization audit

## Phase 1 baseline

- Branch: `refactor/modularize`
- Full test suite: **18 passed**, one existing Starlette/httpx deprecation warning.
- OpenAPI baseline: [openapi.before.json](openapi.before.json), containing 20 paths.
- Current application layout is an early flat implementation. Cross-cutting
  files, schemas, services, models, handlers, middleware, and all HTTP routes
  are directly under `app/`; only analytics and models have packages.

## Current folder map

```text
app/
  analytics/__init__.py, core.py       pandas analysis and dispatcher
  config.py                            settings
  database.py                          SQLAlchemy engine/session/base
  error_handlers.py                    global exception handlers
  exceptions.py                        domain exception hierarchy
  logging_config.py                    logging setup
  main.py                              app wiring, every route, DB orchestration, analytics loading
  messages.py                          user-facing error messages
  middleware.py                        request ID middleware
  models/entities.py                   all SQLAlchemy entities and enums
  schemas.py                           all Pydantic schemas
  services.py                          shared business rules and time/overlap helpers
```

## Size and responsibility findings

Files over 300 lines:

- `app/main.py`: 619 lines; application setup, OpenAPI customization, every
  endpoint, serialization, date handling, analytics frame loading, and
  analytics dispatch.

Functions over 40 lines:

- `app/main.py::_analytics_frames`: 91 lines; loads five model families and
  converts them to pandas frames.
- `app/main.py::analytics`: 47 lines; parses ranges, validates analysis names,
  loads frames, and dispatches analysis.
- `scripts/seed.py::seed_database`: 60 lines; creates all domain seed records.
- `alembic/versions/0001_initial.py::upgrade`: 86 lines; generated migration
  code, intentionally kept as one migration operation.
- `tests/test_api.py::test_manual_entries_and_validation`: 47 lines; test
  scenario setup, not production logic.

## Layering and duplication

- Business rules currently sit in route functions in `main.py`, including
  active-record checks, time-window validation, overlap checks, prayer-date
  checks, and delete confirmation.
- Database queries are embedded throughout route functions in `main.py`.
- `app/analytics/core.py` is mostly pure pandas logic but imports settings
  directly; its dispatcher and envelope construction should move to the
  analytics module service while pure analysis functions are split by concern.
- Session and distraction response conversion is duplicated in `main.py`.
- UTC/date normalization and local-date filtering are duplicated between
  services, `/today`, and analytics frame loading.
- Model enums and all feature models are coupled in one entities file;
  schemas for all features are coupled in one schemas file.

## Constants, strings, and possible dead code

- Route-level values such as 366 days, 16 hours, 24 hours, 1-minute clock
  tolerance, and analytics range names are inline rather than owned by a
  configuration or feature module.
- Several user-facing validation strings are inline in schemas and `main.py`
  instead of using the central messages module.
- No unused production file was conclusively identified in this static pass;
  import/type-check validation during each move will be used to confirm.
- No circular import was observed, but `models/entities.py -> database.py`,
  `main.py -> models/services/analytics`, and the all-in-one route module create
  high coupling and make safe changes difficult.

## Bugs or behavior gaps deliberately not fixed

- The existing analytics implementation returns insufficient data for some
  seeded analyses (for example, trends and weekday/weekend in the current
  frame rules). This refactor preserves that behavior.
- The seed script creates data using UTC dates while the application displays
  configured local dates. This task does not alter seed semantics.
- The existing test warning from the installed Starlette/httpx combination is
  retained.

## Final before/after map

Before, `app/main.py` was a 619-line route, persistence, serialization, and
analytics module. Models, schemas, services, and infrastructure were also
flat files directly under `app/`.

After, infrastructure is under `app/core`, API composition is under
`app/api`, and each domain is under `app/modules/` with models, schemas,
services, and thin routers. Analytics loading is in
`app/modules/analytics/service.py`; pure analyses are split across
`app/analytics/` and use `frames.py`. Alembic discovers models through
`app/db/base.py`. `main.py` now only creates the configured FastAPI
application. `tests/test_architecture.py` enforces the dependency boundaries
and 400-line hard limit.

## Final verification

- Baseline: 18 tests passed.
- Final: 23 tests passed.
- Ruff: clean.
- OpenAPI: matches `docs/openapi.before.json` after ordering and operation-ID
  normalization.
- All application Python files are below the 400-line hard limit.

## Bugs or behavior gaps deliberately not fixed

The existing analytics implementation returns insufficient data for some
seeded analyses (for example, trends and weekday/weekend in the current frame
rules). The seed script creates data using UTC dates while the application
displays configured local dates. The installed Starlette/httpx deprecation
warning remains. These are behavior decisions or pre-existing issues, not
refactor changes.
