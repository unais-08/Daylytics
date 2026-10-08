# Personal Analytics frontend

This is the React/Vite frontend for the local Personal Analytics API.

## Run

```powershell
npm install
npm run dev
```

The API defaults to `http://localhost:8000`. Override it with
`VITE_API_BASE_URL` in a local `.env` file. Start the backend and seed demo data
with `python scripts/seed.py` from the backend directory.

## Commands

```powershell
npm run typecheck
npm run lint
npm run build
npm run gen:api
```

`gen:api` reads the running backend's OpenAPI document and writes generated
types to `src/api/schema.d.ts`.

## Where to find things

`src/api` owns the typed HTTP boundary and error parsing. `src/features` will
own feature-specific hooks and components as the app grows. Shared controls
live in `src/components`, formatting helpers in `src/lib`, and route
composition currently lives in `src/App.tsx`. See `docs/PROGRESS.md` for the
implementation checklist and `docs/DECISIONS.md` for choices that affect
future work.

## Current screens

- **Today**: start and stop work or distraction timers, log prayers, career
  output, and sleep.
- **Dashboard**: choose an analysis and range, then view metrics and charts.
  Filters are stored in the URL so a dashboard view can be shared.
- **History**: add missed sessions or distractions and delete incorrect
  entries.
- **Settings**: export all data or permanently delete it after typing `DELETE`.

The frontend is designed for a 375px mobile viewport first. Buttons have
large tap targets, keyboard focus is visible, and empty/error states include a
clear next action.

This template provides a minimal setup to get React working in Vite with HMR and some ESLint rules.

Currently, two official plugins are available:

- [@vitejs/plugin-react](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react) uses [Oxc](https://oxc.rs)
- [@vitejs/plugin-react-swc](https://github.com/vitejs/vite-plugin-react/blob/main/packages/plugin-react-swc) uses [SWC](https://swc.rs/)

## React Compiler

The React Compiler is not enabled on this template because of its impact on dev & build performances. To add it, see [this documentation](https://react.dev/learn/react-compiler/installation).

## Expanding the ESLint configuration

If you are developing a production application, we recommend updating the configuration to enable type-aware lint rules:

```js
export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...

      // Remove tseslint.configs.recommended and replace with this
      tseslint.configs.recommendedTypeChecked,
      // Alternatively, use this for stricter rules
      tseslint.configs.strictTypeChecked,
      // Optionally, add this for stylistic rules
      tseslint.configs.stylisticTypeChecked,

      // Other configs...
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])

```

You can also install [eslint-plugin-react-x](https://npmx.dev/package/eslint-plugin-react-x) and [eslint-plugin-react-dom](https://npmx.dev/package/eslint-plugin-react-dom) for React-specific lint rules:

```js
// eslint.config.js
import reactX from 'eslint-plugin-react-x'
import reactDom from 'eslint-plugin-react-dom'

export default defineConfig([
  globalIgnores(['dist']),
  {
    files: ['**/*.{ts,tsx}'],
    extends: [
      // Other configs...
      // Enable lint rules for React
      reactX.configs['recommended-typescript'],
      // Enable lint rules for React DOM
      reactDom.configs.recommended,
    ],
    languageOptions: {
      parserOptions: {
        project: ['./tsconfig.node.json', './tsconfig.app.json'],
        tsconfigRootDir: import.meta.dirname,
      },
      // other options...
    },
  },
])

```
