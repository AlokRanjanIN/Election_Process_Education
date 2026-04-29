# Setup

This guide explains environment variables, Google Cloud configuration, Firestore setup, and seed data.

## Backend Environment Variables

The backend reads environment variables in `backend/core/config.py`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `GCP_PROJECT_ID` | `election-platform-dev` | Google Cloud project ID. |
| `GCP_LOCATION` | `asia-south1` | Google Cloud region for Vertex AI and deployment. |
| `ENVIRONMENT` | `development` | Runtime environment name. |
| `CORS_ORIGINS` | `http://localhost:5173,http://localhost:3000` | Comma-separated frontend origins allowed by FastAPI CORS. |
| `VERTEX_LLM_MODEL` | `gemini-1.5-flash-001` | Vertex AI generative model used by the FAQ assistant. |
| `VERTEX_EMBEDDING_MODEL` | `text-embedding-004` | Vertex AI embedding model used for FAQ retrieval. |
| `VERTEX_LLM_TEMPERATURE` | `0.0` | LLM temperature. |
| `RAG_TOP_K` | `5` | Number of retrieved documents for FAQ context. |
| `RAG_MAX_QUERY_LENGTH` | `300` | Maximum FAQ query length. |
| `RATE_LIMIT_FAQ` | `10/minute` | Rate limit for `POST /api/v1/faq/ask`. |
| `RATE_LIMIT_TIMELINE` | `30/minute` | Rate limit for `GET /api/v1/timeline`. |
| `RATE_LIMIT_DEFAULT` | `60/minute` | Default per-IP API rate limit. |

The backend does not use `python-dotenv`. A `.env` file is useful as a reference, but it is not loaded automatically by the application.

## Local Backend Environment

Linux and macOS:

```bash
cd backend
export ENVIRONMENT=development
export GCP_PROJECT_ID=YOUR_GCP_PROJECT_ID
export GCP_LOCATION=asia-south1
export CORS_ORIGINS=http://localhost:5173,http://localhost:3000
export VERTEX_LLM_MODEL=gemini-1.5-flash-001
export VERTEX_EMBEDDING_MODEL=text-embedding-004
export VERTEX_LLM_TEMPERATURE=0.0
export RAG_TOP_K=5
export RAG_MAX_QUERY_LENGTH=300
export RATE_LIMIT_FAQ=10/minute
export RATE_LIMIT_TIMELINE=30/minute
export RATE_LIMIT_DEFAULT=60/minute
```

Windows PowerShell:

```powershell
cd backend
$env:ENVIRONMENT = "development"
$env:GCP_PROJECT_ID = "YOUR_GCP_PROJECT_ID"
$env:GCP_LOCATION = "asia-south1"
$env:CORS_ORIGINS = "http://localhost:5173,http://localhost:3000"
$env:VERTEX_LLM_MODEL = "gemini-1.5-flash-001"
$env:VERTEX_EMBEDDING_MODEL = "text-embedding-004"
$env:VERTEX_LLM_TEMPERATURE = "0.0"
$env:RAG_TOP_K = "5"
$env:RAG_MAX_QUERY_LENGTH = "300"
$env:RATE_LIMIT_FAQ = "10/minute"
$env:RATE_LIMIT_TIMELINE = "30/minute"
$env:RATE_LIMIT_DEFAULT = "60/minute"
```

## Frontend Environment Variables

The frontend reads `VITE_API_BASE_URL` in `frontend/src/api/client.ts`.

| Variable | Default | Purpose |
| --- | --- | --- |
| `VITE_API_BASE_URL` | empty string | Backend API base URL used by Axios. |

For local development, you can leave `VITE_API_BASE_URL` empty because `frontend/vite.config.ts` proxies `/api` requests to `http://localhost:8080`.

For a production frontend build, set it to your backend URL:

```bash
cd frontend
VITE_API_BASE_URL=YOUR_BACKEND_CLOUD_RUN_URL npm run build
```

Windows PowerShell:

```powershell
cd frontend
$env:VITE_API_BASE_URL = "YOUR_BACKEND_CLOUD_RUN_URL"
npm run build
```

## Google Cloud Authentication

Log in to Google Cloud:

```bash
gcloud auth login
gcloud config set project YOUR_GCP_PROJECT_ID
```

Set Application Default Credentials for local backend calls to Firestore, Vertex AI, and Translation:

```bash
gcloud auth application-default login
```

## Enable Google Cloud APIs

```bash
gcloud services enable run.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable translate.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

The existing deployment notes also mention Secret Manager. This codebase does not currently read secrets from Secret Manager directly.

## Firestore Database Setup

Create a Firestore native database in `asia-south1`:

```bash
gcloud firestore databases create --location=asia-south1 --type=firestore-native
```

The backend uses these collection names:

| Collection | Used by |
| --- | --- |
| `timelines` | Timeline lookup endpoint. |
| `user_sessions` | Seed script sample session data. |
| `eci_vector_docs` | FAQ vector retrieval. |

## Firestore Vector Index

The FAQ assistant uses Firestore vector search on the `eci_vector_docs.embedding` field.

Create the vector index:

```bash
gcloud firestore indexes composite create --collection-group=eci_vector_docs --query-scope=COLLECTION --field-config=vector-config='{"dimension":"768","flat": "{}"}',field-path=embedding
```

## Seed Timeline Data

The seed file is `backend/data/seed_timelines.json`.

Dry run:

```bash
cd backend
python -m scripts.seed_firestore --dry-run
```

Write data to Firestore:

```bash
cd backend
python -m scripts.seed_firestore
```

## Ingest FAQ Documents

The document seed file is `backend/data/seed_eci_docs.json`.

Dry run:

```bash
cd backend
python -m scripts.ingest --data-file data/seed_eci_docs.json --dry-run
```

Generate embeddings and write documents to Firestore:

```bash
cd backend
python -m scripts.ingest --data-file data/seed_eci_docs.json
```

The non-dry-run ingestion command calls Vertex AI and Firestore. It requires Google Cloud authentication and enabled APIs.

## Next Step

Continue with [Usage](usage.md).
