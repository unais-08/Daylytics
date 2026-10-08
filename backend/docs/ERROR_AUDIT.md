# Error audit

This audit records the behavior before the error-handling work.

## Endpoint audit

| Endpoint | Current failures | Current response |
|---|---|---|
| `GET /`, `GET /health` | No expected domain failures | `200` JSON |
| `GET /export` | Database errors are unhandled | Raw `500` |
| `DELETE /data` | Missing `confirm=true` | `400` FastAPI `{"detail": ...}` |
| `POST /sessions/start` | Active session | `409` FastAPI detail; database errors are raw `500` |
| `POST /sessions/{id}/stop` | Missing id, already stopped | `404`/`409` FastAPI detail; arithmetic/database errors can be raw `500` |
| `POST /sessions` | Pydantic validation, invalid times | `422` FastAPI validation body; database errors are raw `500` |
| `GET /sessions` | Invalid query values are loosely accepted; database errors | Usually `200` or raw `500` |
| `DELETE /sessions/{id}` | Missing id | `404` FastAPI detail |
| `POST /distractions/start` | Active distraction | `409` FastAPI detail |
| `POST /distractions/{id}/stop` | Missing id, already stopped | `404`/`409` FastAPI detail |
| `POST /distractions` | Pydantic validation, invalid times | `422` FastAPI validation body |
| `GET /distractions` | Database errors | Raw `500` |
| `DELETE /distractions/{id}` | Missing id | `404` FastAPI detail |
| `POST /sleep` | Pydantic validation | `422` FastAPI validation body |
| `GET /sleep` | Database errors | Raw `500` |
| `DELETE /sleep/{id}` | Missing id | `404` FastAPI detail |
| `POST /career-output` | Pydantic validation, database constraints | `422` or raw `500` |
| `GET /career-output` | Database errors | Raw `500` |
| `DELETE /career-output/{id}` | Missing id | `404` FastAPI detail |
| `PUT /prayers/{date}/{prayer}` | Invalid date/enum/status, duplicate race | `422` FastAPI validation or raw database `500` |
| `DELETE /prayers/{date}/{prayer}` | Missing id | `404` FastAPI detail |
| `GET /prayers` | Invalid date, database errors | `422` or raw `500` |
| `GET /today` | Database and timezone-related runtime errors | Raw `500` |
| `GET /analytics/{kind}` | Invalid range/name/date, pandas/database failures | `404`/`422` FastAPI detail or raw `500` |

Unknown routes and unsupported methods use Starlette's default `{"detail": ...}`
responses. Request IDs are not currently generated or returned.

## Unhandled and inconsistent cases

- Pydantic validation errors expose FastAPI's internal error structure and
  technical messages rather than stable application codes.
- `HTTPException` bodies use a different `detail` shape from validation errors.
- SQLAlchemy `IntegrityError`, `OperationalError`, and pandas/runtime
  exceptions are not handled globally.
- Database sessions close through the context manager but do not explicitly
  roll back when a request fails after a write.
- Domain routes return generic `404` messages instead of stable resource codes.
- There is no centralized logging or request correlation ID.
- Direct model/database writes can bypass API validators for time ordering and
  duplicate constraints.
- Analytics rejects some invalid inputs with generic route errors and has no
  consistent error envelope.

## Target state

All failures will use the standard `error` envelope, a stable code, a
human-readable actionable message, safe structured details, and a request ID
also present in `X-Request-ID`.

## After implementation

- All application routes now raise stable domain errors instead of raw
  `HTTPException` responses.
- Validation, unknown routes, unsupported methods, database integrity failures,
  database availability failures, and unexpected exceptions use the same
  envelope.
- Request IDs are generated or safely accepted from `X-Request-ID`, returned
  on every response, and included in error logs.
- Database sessions explicitly roll back when request processing fails.
- Manual session and distraction entries reject future, excessive, and
  overlapping time windows.
- Sleep duration, prayer dates, analytics names, filters, and date ranges have
  actionable validation errors.
- OpenAPI documents the common error response schema for every operation.
