# Frontend

 React + Tailwind website for EEG upload, tri-class assessment monitoring, and dementia classification reporting.

## Highlights

- Dashboard for upload, run, and result review
- Pipeline page that shows model steps and key metrics
- Project page with study context and model notes
- Tri-class outputs for AD, HC, and FTD with confidence and optional risk score
- Run history saved in browser storage
- Download JSON reports or copy JSON from the summary panel
- Clean separation across pages, components, context, services, constants, and utils

## Route map

- `/` Dashboard
- `/pipeline` Inference pipeline overview
- `/project` Project and proposal context

## Project structure

```text
src/
  app/          Global shell and layout
  pages/        Route-level screens
  components/   Reusable UI and dashboard sections
  context/      Shared inference state and actions
  services/     Backend API integration
  constants/    Static app config/content
  utils/        Pure helper utilities
```

## Quick start

```bash
npm install
npm run dev
```

App runs at the Vite URL (usually `http://localhost:5173`).

## Environment

Create `.env` in `frontend/` (or copy from `.env.example`):

```bash
VITE_API_URL=http://127.0.0.1:8000/predict
```

## Commands

```bash
npm run dev
npm run lint
npm run build
```
