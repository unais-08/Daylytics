# Error codes

| Code | Status | Meaning | Example message |
|---|---:|---|---|
| `VALIDATION_ERROR` | 422 | Request fields are invalid | Some fields are invalid. |
| `ROUTE_NOT_FOUND` | 404 | URL does not exist | That URL was not found. Check the path and try again. |
| `METHOD_NOT_ALLOWED` | 405 | HTTP method is unsupported | That action is not supported for this URL. |
| `CONFIRMATION_REQUIRED` | 400 | Destructive action lacks confirmation | Pass confirm=true to delete all personal data. |
| `DUPLICATE_ENTRY` | 409 | Record conflicts with an existing unique record | This record already exists. Review the existing entry and try again. |
| `DATABASE_UNAVAILABLE` | 503 | Database cannot be reached | The database is temporarily unavailable. Please try again. |
| `INTERNAL_ERROR` | 500 | Unexpected server failure | Something went wrong on the server. Please try again. |
| `SESSION_NOT_FOUND` | 404 | Work session ID does not exist | That work session was not found. Check the session ID and try again. |
| `DISTRACTION_NOT_FOUND` | 404 | Distraction ID does not exist | That distraction was not found. Check the distraction ID and try again. |
| `SLEEP_LOG_NOT_FOUND` | 404 | Sleep log ID does not exist | That sleep log was not found. Check the sleep log ID and try again. |
| `CAREER_OUTPUT_NOT_FOUND` | 404 | Career entry ID does not exist | That career entry was not found. Check the entry ID and try again. |
| `SESSION_ALREADY_ACTIVE` | 409 | Another work session is running | A work session is already running. Stop it before starting a new one. |
| `DISTRACTION_ALREADY_ACTIVE` | 409 | Another distraction is running | A distraction is already running. Stop it before starting a new one. |
| `SESSION_ALREADY_STOPPED` | 409 | Session is already stopped | That work session has already stopped. Choose a running session instead. |
| `DISTRACTION_ALREADY_STOPPED` | 409 | Distraction is already stopped | That distraction has already stopped. Choose a running distraction instead. |
| `INVALID_TIME_RANGE` | 422 | End is not after start | The end time must be after the start time. |
| `FUTURE_TIME_NOT_ALLOWED` | 422 | Timestamp is in the future | Times in the future are not allowed. Use the current time or an earlier time. |
| `SESSION_TOO_LONG` | 422 | Session exceeds 16 hours | A work session cannot be longer than 16 hours. Check the times and try again. |
| `SLEEP_DURATION_IMPLAUSIBLE` | 422 | Sleep is outside 1–24 hours | Sleep duration must be between 1 and 24 hours. Check the times and try again. |
| `OVERLAPPING_SESSION` | 422 | Work session overlaps another | This work session overlaps an existing session. Adjust the times and try again. |
| `OVERLAPPING_DISTRACTION` | 422 | Distraction overlaps another | This distraction overlaps an existing distraction. Adjust the times and try again. |
