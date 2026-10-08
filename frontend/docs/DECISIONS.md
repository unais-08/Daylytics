# Frontend decisions

- Server state is managed with TanStack Query. There is no global client-side
  store because the backend is the source of truth.
- The API client uses the browser `fetch` API and preserves the backend error
  code, message, and request ID for user-facing feedback.
- Today is intentionally the primary route. Every frequent action is a
  visible button or chip and does not require a separate form page.
- The first dashboard iteration renders the backend result safely as key
  metrics and a readable JSON view. Dedicated chart components will be added
  per analysis once their response shapes are generated from OpenAPI.
