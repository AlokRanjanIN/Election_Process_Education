# Architecture

This project has a React frontend and a FastAPI backend. The backend integrates with Google Cloud services for Firestore data, vector retrieval, Vertex AI generation, and translation.

## High-Level Design

```text
Browser
  |
  | React + Vite frontend
  |
  | HTTP JSON requests
  v
FastAPI backend
  |
  | Routers in backend/api
  v
Service layer in backend/services
  |
  +--> Deterministic eligibility rules
  +--> Deterministic guide state machine
  +--> Firestore timeline query
  +--> FAQ security, translation, retrieval, and generation
```

## Backend Modules

| Module | Purpose |
| --- | --- |
| `backend/main.py` | Creates the FastAPI app, configures CORS and middleware, registers routers, and defines system endpoints. |
| `backend/api/` | FastAPI routers for eligibility, guide, timeline, and FAQ. |
| `backend/models/` | Pydantic request and response models. |
| `backend/services/` | Business logic and Google Cloud service calls. |
| `backend/core/config.py` | Environment-based settings. |
| `backend/core/firebase.py` | Firebase Admin SDK and Firestore client initialization. |
| `backend/core/middleware.py` | SlowAPI rate limiting and request logging. |
| `backend/core/security.py` | Prompt-injection detection, query validation, sanitization, and PII scrubbing. |
| `backend/scripts/` | Firestore seeding and document ingestion scripts. |

## Frontend Modules

| Module | Purpose |
| --- | --- |
| `frontend/src/App.tsx` | Navigation, routes, and page layout. |
| `frontend/src/components/` | Page-level React components. |
| `frontend/src/api/client.ts` | Axios API calls and TypeScript types. |
| `frontend/src/i18n.ts` | Language setup. |
| `frontend/src/locales/` | English and Hindi translations. |
| `frontend/src/index.css` | Tailwind component classes and shared styles. |

## Eligibility Flow

```text
EligibilityPage
  -> evaluateEligibility()
  -> POST /api/v1/eligibility/evaluate
  -> api/eligibility.py
  -> services/eligibility_service.py
  -> EligibilityResponse
```

The eligibility service checks:

1. Indian citizenship.
2. Age as of January 1 of the current year.
3. NRI status for form selection.

It returns `Form 6` for eligible domestic voters and `Form 6A` for eligible NRI voters.

## Guide Flow

```text
GuidePage
  -> getGuideNextStep()
  -> GET /api/v1/guide/next-step
  -> api/guide.py
  -> services/guide_service.py
  -> GuideResponse
```

The guide is a deterministic state machine:

```text
INIT
DOCUMENTS_CHECKLIST
FORM_SELECTION
FORM_DOWNLOADED
FORM_FILLING
FORM_SUBMITTED
VERIFICATION
COMPLETE
```

The server does not store guide progress. The client sends the current state and receives the next state.

## Timeline Flow

```text
TimelinePage
  -> getTimeline()
  -> GET /api/v1/timeline
  -> api/timeline.py
  -> services/timeline_service.py
  -> Firestore timelines collection
  -> TimelineResponse[]
```

Timeline queries filter by:

- `state_code`
- optional `constituency_id`

Events are sorted by date before returning to the client.

## FAQ Flow

```text
FAQPage
  -> askFAQ()
  -> POST /api/v1/faq/ask
  -> api/faq.py
  -> security checks
  -> optional translation to English
  -> services/rag_service.py
  -> Vertex AI embedding
  -> Firestore vector search
  -> grounded prompt
  -> Vertex AI generation
  -> response parsing
  -> optional translation back to user locale
  -> FAQResponse
```

The FAQ endpoint applies this security chain:

1. Sanitize input.
2. Validate query length.
3. Detect prompt-injection patterns.
4. Detect and scrub PII.
5. Translate non-English input to English.
6. Run retrieval and generation.
7. Translate response back when needed.

## Data Storage

| Collection | Fields used by code | Purpose |
| --- | --- | --- |
| `timelines` | `state_code`, `constituency_id`, `events` | Stores election event timelines. |
| `eci_vector_docs` | `title`, `content`, `url`, `embedding` | Stores FAQ source documents and vectors. |
| `user_sessions` | `session_id`, `current_state`, `last_updated`, `context` | Seeded with sample session data, but not used by current API routes. |

## External Services

| Service | Used for |
| --- | --- |
| Firestore | Timeline data and FAQ vector documents. |
| Vertex AI text embeddings | Embedding FAQ queries and documents. |
| Vertex AI Gemini | Generating grounded FAQ answers. |
| Google Cloud Translation API | Translating non-English FAQ queries and answers. |
| Google Cloud Run | Container deployment target. |

## Deployment Shape

The repository contains two Dockerfiles:

| Dockerfile | Purpose |
| --- | --- |
| `backend/Dockerfile` | Runs FastAPI with Uvicorn on `$PORT`, default `8080`. |
| `frontend/Dockerfile` | Builds the Vite app and serves it with Nginx on port `8080`. |

The GitHub Actions workflow at `.github/workflows/deploy.yml` tests and deploys the backend service to Cloud Run on pushes to `main`.
