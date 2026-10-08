# Frontend guide for the Personal Analytics API

This document is the practical handoff for building the React frontend.
The backend is a single-user, local-first FastAPI application. It has no
authentication in the MVP and does not send personal data to external
services.

## 1. Run the backend

From `backend/`:

```powershell
.\venv\Scripts\Activate.ps1
uvicorn app.main:app --reload
```

Use:

- API base URL: `http://127.0.0.1:8000`
- Swagger UI: `http://127.0.0.1:8000/docs`
- OpenAPI schema: `http://127.0.0.1:8000/openapi.json`
- Frontend dev origin: `http://localhost:5173`

The API has no login flow. Store the base URL in a frontend environment
variable, for example `VITE_API_BASE_URL`.

## 2. Important frontend rules

### Dates and times

- Send timestamps as ISO-8601 values.
- Prefer UTC values with a `Z` suffix when sending datetimes.
- The backend stores timestamps as UTC.
- The configured user timezone is `Asia/Kolkata`.
- Display timestamps in the user’s local timezone, not as raw UTC.
- A session belongs to the local date of its start time.
- A sleep log belongs to the local date of its wake time.

### Error handling

Every failed request has this shape:

```json
{
  "error": {
    "code": "SESSION_ALREADY_ACTIVE",
    "message": "A work session is already running. Stop it before starting a new one.",
    "details": {
      "conflicting_id": 12
    },
    "request_id": "8f3c5f3e-42b9-4f32-9ef4-f0f2b0f5d1c2"
  }
}
```

The same request ID is also in the `X-Request-ID` response header. The
frontend should:

1. Parse `response.error.code` for predictable UI behavior.
2. Show `response.error.message` to the user.
3. Use `response.error.details` for field-level errors or conflicting IDs.
4. Keep the request ID in logs or support reports.
5. Never show a stack trace or raw server response.

For `VALIDATION_ERROR`, field errors are available here:

```json
{
  "error": {
    "code": "VALIDATION_ERROR",
    "message": "Some fields are invalid.",
    "details": {
      "fields": [
        {
          "field": "focus_score",
          "message": "This value must be at most 5."
        }
      ]
    },
    "request_id": "..."
  }
}
```

## 3. Recommended screen structure

### Dashboard / Today

Load `GET /today` when the home screen opens. Refresh it after every start, stop, or new log.

Suggested sections:

- Active work timer
- Active distraction timer
- Today’s work and distraction totals
- Quick career-output actions
- Sleep summary or link to sleep logging

### Logging

Use small forms and one-click actions:

- Start/stop work session
- Start/stop distraction
- Add manual work session
- Add retroactive distraction
- Add sleep log
- Add career output

### Analytics

Use a shared range selector for `today`, `7d`, `30d`, and `custom`.
Show the `data_sufficiency.message` near every chart so sparse data is not
mistaken for a strong personal pattern.

## 4. Endpoint reference

### Health

```http
GET /health
```

Response:

```json
{"status": "ok"}
```

### Work sessions

#### Start a timer

```http
POST /sessions/start
Content-Type: application/json
```

```json
{"activity": "DSA"}
```

Allowed activities:

```text
DSA
PROJECT
JOB_APPLICATION
INTERVIEW_PREP
LEARNING
OTHER
```

#### Stop a timer

```http
POST /sessions/{id}/stop
```

```json
{
  "focus_score": 4,
  "deep_work": true
}
```

`deep_work` is optional. If omitted, the backend derives it from the session
duration using the configured threshold.

#### Add a manual session

```http
POST /sessions
```

```json
{
  "activity": "PROJECT",
  "start_time": "2026-10-08T08:00:00Z",
  "end_time": "2026-10-08T09:30:00Z",
  "focus_score": 4,
  "deep_work": true
}
```

#### List sessions

```http
GET /sessions
GET /sessions?start_date=2026-10-01&end_date=2026-10-08&activity=DSA
```

Session response:

```json
{
  "id": 1,
  "activity": "DSA",
  "start_time": "2026-10-08T08:00:00",
  "end_time": "2026-10-08T09:30:00",
  "deep_work": true,
  "focus_score": 4,
  "duration_minutes": 90.0
}
```

### Distractions

Allowed categories:

```text
YOUTUBE
INSTAGRAM
GAMING
RANDOM_BROWSING
PHONE
OTHER
```

Start and stop:

```http
POST /distractions/start
POST /distractions/{id}/stop
```

```json
{"category": "YOUTUBE"}
```

Retroactive entry by duration:

```http
POST /distractions
```

```json
{
  "category": "PHONE",
  "minutes": 20
}
```

Or provide explicit `start_time` and `end_time`, but do not send both forms.

### Sleep

```http
POST /sleep
```

```json
{
  "sleep_start": "2026-10-07T23:00:00Z",
  "wake_time": "2026-10-08T06:30:00Z"
}
```

Other endpoints:

```http
GET /sleep
DELETE /sleep/{id}
```

### Career output

```http
POST /career-output
```

```json
{
  "type": "DSA_PROBLEMS",
  "count": 2,
  "note": "Arrays and hashing"
}
```

Allowed types:

```text
DSA_PROBLEMS
PROJECT_WORK
APPLICATIONS
INTERVIEW
MOCK_INTERVIEW
```

`logged_at` is optional and defaults to the current time.

## 5. Analytics

All analytics endpoints return:

```json
{
  "analysis": "deep-work",
  "data_sufficiency": {
    "days_with_data": 12,
    "level": "early",
    "message": "Early pattern, treat cautiously."
  },
  "result": {},
  "range": {
    "name": "30d",
    "start_date": "2026-09-09",
    "end_date": "2026-10-08"
  }
}
```

Request format:

```http
GET /analytics/{analysis}?range=30d
GET /analytics/{analysis}?range=custom&start_date=2026-09-01&end_date=2026-10-08
```

Available analyses:

| Endpoint | Main result fields |
|---|---|
| `/analytics/overview` | `deep_work_minutes`, `distraction_minutes`, `career_units` |
| `/analytics/time-leaks` | `total_minutes`, `by_category`, `top_category` |
| `/analytics/deep-work` | `total_minutes`, `session_count`, daily averages, longest session, average focus |
| `/analytics/best-worst-days` | `days`, `top_3`, `bottom_3` |
| `/analytics/focus-by-time` | `by_hour`, `by_period` |
| `/analytics/career-output` | `total_units`, `by_type` |
| `/analytics/weekday-weekend` | weekday/weekend deep work and distractions |
| `/analytics/sleep-focus` | `correlation`, with label `correlation, not causation` |
| `/analytics/trends` | `daily_deep_work`, `weekly_distraction` |

If there is no data, analytics still return HTTP 200. Render an empty state
using the returned `data_sufficiency.message`; do not treat it as a network
failure.

## 6. Data export and reset

Export all data:

```http
GET /export
```

Delete all data:

```http
DELETE /data?confirm=true
```

Do not place the delete action beside normal logging controls. Put it behind a
settings screen and a confirmation dialog.

## 7. Suggested frontend API client

Use one shared client rather than calling `fetch` throughout components:

```ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL ?? "http://127.0.0.1:8000";

export async function apiRequest<T>(
  path: string,
  options: RequestInit = {},
): Promise<T> {
  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers: {
      "Content-Type": "application/json",
      ...options.headers,
    },
  });

  const body = await response.json().catch(() => null);
  if (!response.ok) {
    throw body?.error ?? {
      code: "NETWORK_ERROR",
      message: "The server could not be reached. Please try again.",
      request_id: response.headers.get("X-Request-ID"),
    };
  }
  return body as T;
}
```

Keep TypeScript types generated from `/openapi.json` where possible. The
backend’s authoritative API schemas are in Swagger/OpenAPI, not in this guide.

## 8. Testing frontend integration manually

1. Start the backend.
2. Run `python scripts/seed.py` from `backend/` for demo data.
3. Open the frontend at `http://localhost:5173`.
4. Check `/today` and the overview card first.
5. Try starting a second session to verify the friendly conflict message.
6. Check an analytics empty state after `DELETE /data?confirm=true`.
7. Re-run the seed script to restore the demo dataset.
