# Frontend API contract

The API runs at `http://localhost:8000` and permits requests from
`http://localhost:5173`. Start it with:

```powershell
uvicorn app.main:app --reload
```

All timestamps are ISO-8601 UTC values. Analytics endpoints accept
`range=today|7d|30d|custom`; custom ranges also require `start_date` and
`end_date`. Analytics responses use:

```json
{
  "analysis": "overview",
  "range": {"name": "30d", "start_date": "2026-09-09", "end_date": "2026-10-08"},
  "data_sufficiency": {"days_with_data": 12, "level": "early", "message": "..."},
  "result": {}
}
```

Use `GET /openapi.json` for the generated request and response schemas.

For the complete frontend handoff, including workflows, screen suggestions,
payload examples, analytics behavior, and error handling, see
[FRONTEND_BACKEND_GUIDE.md](FRONTEND_BACKEND_GUIDE.md).

## Postman

Import [personal-analytics.postman_collection.json](personal-analytics.postman_collection.json)
into Postman. It uses `{{baseUrl}} = http://127.0.0.1:8000` and includes the
health check, logging flows, prayers, analytics, export, and confirmed delete
requests.
