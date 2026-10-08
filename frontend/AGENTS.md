# Frontend agent guide

## Purpose

This frontend is a mobile-first React application for the local Personal
Analytics FastAPI backend. Today is the fast logging surface; Dashboard is for
reflection, not pressure.

## Structure

- `src/api/`: fetch client, backend error parsing, generated OpenAPI types.
- `src/features/`: feature-owned UI and hooks, such as analytics charts.
- `src/components/`: reusable presentation primitives.
- `src/lib/`: small shared formatting functions only.
- `src/App.tsx`: route composition and current page-level workflows.
- `docs/`: progress and implementation decisions.

## Commands

```powershell
npm install
npm run dev
npm run lint
npm run typecheck
npm run build
npm run gen:api
```

## Rules

- Use TanStack Query for server state; do not add Redux, Zustand, or another
  global store.
- Use the generated OpenAPI types and the existing API client; do not invent
  endpoint shapes.
- Keep API failures human-readable and preserve the backend error code and
  request ID.
- Keep frequent Today actions to one to three taps.
- Every interactive control needs a visible focus state and an accessible
  label when its purpose is icon-only.
- Prefer existing components and formatters before creating new shared helpers.

## Adding a feature

1. Confirm the endpoint and response in the backend OpenAPI document.
2. Add or update types and methods in `src/api/`.
3. Put feature-specific UI in `src/features/<feature>/`.
4. Use React Query for loading, mutation, invalidation, and retry behavior.
5. Add loading, empty, error, and success states.
6. Run lint, typecheck, and build before handing off.

## Adding a chart

1. Capture the real seeded and empty response shapes.
2. Add a focused chart branch or component under `src/features/analytics/`.
3. Give the chart a plain-English question as its title.
4. Hide missing buckets and show an explicit insufficient-data state.
5. Check the chart at mobile width and run the full validation commands.

## Do not

- Put database logic or backend business rules in the frontend.
- Use `any`, `@ts-ignore`, or disabled lint rules to bypass errors.
- Add external analytics, tracking, or personal-data services.
- Use color alone to communicate a status.
- Add gamification, auth, notifications, or unrelated product features.
