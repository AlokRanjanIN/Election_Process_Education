# Frontend

The frontend is a React application built with Vite and TypeScript.

## Main Files

| Path | Purpose |
| --- | --- |
| `frontend/src/main.tsx` | React entry point. |
| `frontend/src/App.tsx` | Router, navigation bar, footer, and route definitions. |
| `frontend/src/api/client.ts` | Axios client, TypeScript request/response types, and API functions. |
| `frontend/src/i18n.ts` | i18next setup for English and Hindi. |
| `frontend/src/index.css` | Tailwind imports, shared component classes, animations, and spinner styles. |
| `frontend/vite.config.ts` | Vite, React plugin, PWA plugin, dev server proxy. |
| `frontend/tailwind.config.js` | Tailwind theme colors, fonts, and spacing. |
| `frontend/nginx.conf` | Nginx config for serving the production build in Docker. |

## Routes

Routes are defined in `frontend/src/App.tsx`.

| Route | Component | Purpose |
| --- | --- | --- |
| `/` | `HomePage` | Landing page with links to workflows. |
| `/eligibility` | `EligibilityPage` | Eligibility form and result display. |
| `/guide` | `GuidePage` | Registration guide stepper. |
| `/timeline` | `TimelinePage` | Timeline search form and event list. |
| `/faq` | `FAQPage` | FAQ question form, answer, citations, voice input, and read-aloud. |

## Frontend Screenshots

Screenshot assets are stored in the repository-level `screenshots/` folder.

| Page | Screenshot |
| --- | --- |
| Home | `screenshots/1_Home.png` |
| Eligibility | `screenshots/2_Eligibility.png` |
| Registration Guide | `screenshots/3_Guide.png` |
| Timeline | `screenshots/4_Timeline.png` |
| FAQ | `screenshots/5_Ask.png` |

## Components

| Component | File | Backend API used |
| --- | --- | --- |
| `HomePage` | `src/components/HomePage.tsx` | None |
| `EligibilityPage` | `src/components/EligibilityPage.tsx` | `POST /api/v1/eligibility/evaluate` |
| `GuidePage` | `src/components/GuidePage.tsx` | `GET /api/v1/guide/next-step` |
| `TimelinePage` | `src/components/TimelinePage.tsx` | `GET /api/v1/timeline` |
| `FAQPage` | `src/components/FAQPage.tsx` | `POST /api/v1/faq/ask` |

## API Integration

The frontend API client is in `frontend/src/api/client.ts`.

It exports:

| Function | Endpoint |
| --- | --- |
| `evaluateEligibility(data)` | `POST /api/v1/eligibility/evaluate` |
| `getGuideNextStep(currentState)` | `GET /api/v1/guide/next-step` |
| `getTimeline(stateCode, constituencyId)` | `GET /api/v1/timeline` |
| `askFAQ(data)` | `POST /api/v1/faq/ask` |

Axios uses:

```ts
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || ''
```

During local development, `VITE_API_BASE_URL` can be empty because Vite proxies `/api` to `http://localhost:8080`.

## State Management

The frontend uses React component state with `useState` and `useEffect`. There is no Redux, Zustand, React Query, or global application state store in the current codebase.

Important local state examples:

| Component | State |
| --- | --- |
| `EligibilityPage` | Form values, loading state, error text, eligibility result. |
| `GuidePage` | Current guide response, history stack, loading state, error text. |
| `TimelinePage` | State code, constituency ID, timeline results, loading state, error text. |
| `FAQPage` | Query text, FAQ answer, loading state, error text. |

## Internationalization

The frontend uses:

- `i18next`
- `react-i18next`
- `i18next-browser-languagedetector`

Translation files:

```text
frontend/src/locales/en.json
frontend/src/locales/hi.json
```

The language toggle in the navigation bar switches between:

| UI language | i18next language |
| --- | --- |
| English | `en` |
| Hindi | `hi` |

The FAQ page maps frontend language to backend locale:

| Frontend language | Backend locale |
| --- | --- |
| `en` | `en-IN` |
| `hi` | `hi-IN` |

## Styling

The application uses Tailwind CSS and shared component classes in `frontend/src/index.css`.

Shared classes include:

| Class | Purpose |
| --- | --- |
| `.btn-primary` | Primary button styling. |
| `.btn-secondary` | Secondary button styling. |
| `.card` | White card container. |
| `.input-field` | Input, select, and textarea styling. |
| `.status-eligible` | Green success result box. |
| `.status-ineligible` | Red error or ineligible result box. |
| `.spinner` | Loading spinner. |

## PWA Configuration

`frontend/vite.config.ts` uses `vite-plugin-pwa`.

The manifest includes:

- Name: `Indian Election Process Education Assistant`
- Short name: `Election Guide`
- Display mode: `standalone`
- Theme color: `#1a237e`

The config references `/icon-192x192.png` and `/icon-512x512.png`. Those icon files are not currently present in the repository.

## Run Frontend Locally

```bash
cd frontend
npm ci
npm run dev
```

Open:

```text
http://localhost:5173
```

## Build Frontend

```bash
cd frontend
npm ci
npm run build
```

## Preview Build

```bash
cd frontend
npm run preview
```
