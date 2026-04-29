# Deployment Guide — Indian Election Process Education Assistant

## Prerequisites

Before deploying, ensure you have the following:

1. **Google Cloud SDK** (`gcloud`) installed and configured
2. **Docker** installed locally (for testing container builds)
3. **GCP Project** with billing enabled
4. **Python 3.11+** installed locally (for development/testing)
5. **Node.js 18+** (for frontend builds)

---

## Step 1: GCP Project Setup

### 1.1 Set Your Project

```bash
gcloud config set project [YOUR_PROJECT_ID]
```

### 1.2 Enable Required APIs

```bash
gcloud services enable \
  run.googleapis.com \
  firestore.googleapis.com \
  aiplatform.googleapis.com \
  translate.googleapis.com \
  cloudbuild.googleapis.com \
  artifactregistry.googleapis.com \
  secretmanager.googleapis.com
```

### 1.3 Create Firestore Database

```bash
gcloud firestore databases create \
  --location=asia-south1 \
  --type=firestore-native
```

### 1.4 Create Firestore Vector Index

The `eci_vector_docs` collection requires a vector index for nearest-neighbor search:

```bash
gcloud firestore indexes composite create \
  --collection-group=eci_vector_docs \
  --query-scope=COLLECTION \
  --field-config=vector-config='{"dimension":"768","flat": "{}"}',field-path=embedding
```

---

## Step 2: Configure IAM Permissions

### 2.1 Get the Default Cloud Run Service Account

```bash
PROJECT_NUMBER=$(gcloud projects describe [YOUR_PROJECT_ID] --format="value(projectNumber)")
SA_EMAIL="${PROJECT_NUMBER}-compute@developer.gserviceaccount.com"
```

### 2.2 Grant Required Roles

```bash
# Firestore read access
gcloud projects add-iam-policy-binding [YOUR_PROJECT_ID] \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/datastore.viewer"

# Vertex AI access
gcloud projects add-iam-policy-binding [YOUR_PROJECT_ID] \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/aiplatform.user"

# Translation API access
gcloud projects add-iam-policy-binding [YOUR_PROJECT_ID] \
  --member="serviceAccount:${SA_EMAIL}" \
  --role="roles/cloudtranslate.user"
```

---

## Step 3: Seed Data

### 3.1 Set Up Local Environment

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### 3.2 Authenticate Locally

```bash
gcloud auth application-default login
```

### 3.3 Seed Firestore Collections

```bash
# Set project ID
export GCP_PROJECT_ID=[YOUR_PROJECT_ID]
export GCP_LOCATION=asia-south1

# Seed timeline data
python -m scripts.seed_firestore

# Ingest ECI documents (generates embeddings + uploads to vector store)
python -m scripts.ingest --data-file data/seed_eci_docs.json
```

To test seeding without writing to Firestore:

```bash
python -m scripts.seed_firestore --dry-run
python -m scripts.ingest --data-file data/seed_eci_docs.json --dry-run
```

---

## Step 4: Run Tests Locally

```bash
cd backend

# Install test dependencies
pip install -r requirements.txt

# Run all tests with coverage
pytest tests/ -v --cov=. --cov-report=term-missing

# Run specific test suites
pytest tests/test_eligibility.py -v    # Eligibility rules + API
pytest tests/test_guide.py -v          # State machine + API
pytest tests/test_timeline.py -v       # Timeline queries + API
pytest tests/test_faq.py -v            # RAG pipeline + API
pytest tests/test_security.py -v       # Security + system endpoints
```

---

## Step 5: Local Development Server

```bash
cd backend

# Set environment variables
export ENVIRONMENT=development
export GCP_PROJECT_ID=[YOUR_PROJECT_ID]
export GCP_LOCATION=asia-south1
export CORS_ORIGINS=http://localhost:5173,http://localhost:3000

# Start FastAPI dev server
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

The API will be available at:
- **API Docs:** http://localhost:8080/docs
- **ReDoc:** http://localhost:8080/redoc
- **Health Check:** http://localhost:8080/health

---

## Step 6: Build & Test Docker Container

```bash
cd backend

# Build the container
docker build -t election-api .

# Run locally
docker run -p 8080:8080 \
  -e GCP_PROJECT_ID=[YOUR_PROJECT_ID] \
  -e GCP_LOCATION=asia-south1 \
  -e ENVIRONMENT=staging \
  -e CORS_ORIGINS=http://localhost:5173 \
  -e GOOGLE_APPLICATION_CREDENTIALS=/app/credentials.json \
  -v ~/.config/gcloud/application_default_credentials.json:/app/credentials.json \
  election-api
```

---

## Step 7: Deploy Backend to Cloud Run

### 7.1 Build and Push to Artifact Registry

```bash
cd backend

# Using Cloud Build (recommended)
gcloud builds submit --tag gcr.io/[YOUR_PROJECT_ID]/election-api
```

### 7.2 Deploy to Cloud Run

```bash
gcloud run deploy election-api \
  --image gcr.io/[YOUR_PROJECT_ID]/election-api \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated \
  --memory 1024Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 100 \
  --concurrency 80 \
  --cpu-throttling \
  --set-env-vars "GCP_PROJECT_ID=[YOUR_PROJECT_ID],GCP_LOCATION=asia-south1,ENVIRONMENT=production,CORS_ORIGINS=https://your-frontend-domain.web.app"
```

### 7.3 Verify Deployment

```bash
# Get the service URL
SERVICE_URL=$(gcloud run services describe election-api \
  --platform managed \
  --region asia-south1 \
  --format "value(status.url)")

# Test health check
curl "${SERVICE_URL}/health"

# Test eligibility endpoint
curl -X POST "${SERVICE_URL}/api/v1/eligibility/evaluate" \
  -H "Content-Type: application/json" \
  -d '{"dob": "2000-01-15", "is_citizen": true, "state_of_residence": "MH", "is_nri": false}'

# Test guide endpoint
curl "${SERVICE_URL}/api/v1/guide/next-step?current_state=INIT"
```

---

## Step 8: Deploy Frontend (Optional)

### 8.1 Build Frontend

```bash
cd frontend
npm install
npm run build
```

### 8.2 Deploy to Cloud Storage + CDN

```bash
# Create a bucket for the frontend
gsutil mb -l asia-south1 gs://[YOUR_PROJECT_ID]-frontend

# Upload build output
gsutil -m rsync -r dist/ gs://[YOUR_PROJECT_ID]-frontend

# Make public
gsutil iam ch allUsers:objectViewer gs://[YOUR_PROJECT_ID]-frontend

# Configure as website
gsutil web set -m index.html -e index.html gs://[YOUR_PROJECT_ID]-frontend
```

---

## Step 9: Configure CI/CD (GitHub Actions)

The workflow file is located at `.github/workflows/deploy.yml`.

### 9.1 Set Up Workload Identity Federation

```bash
# Create Workload Identity Pool
gcloud iam workload-identity-pools create "github-pool" \
  --location="global" \
  --display-name="GitHub Actions Pool"

# Create Provider
gcloud iam workload-identity-pools providers create-oidc "github-provider" \
  --location="global" \
  --workload-identity-pool="github-pool" \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"
```

### 9.2 Set GitHub Secrets

In your GitHub repository settings, add these secrets:
- `GCP_PROJECT_ID`: Your GCP project ID
- `WIF_PROVIDER`: Workload Identity Federation provider resource name
- `WIF_SERVICE_ACCOUNT`: Service account email for deployments

---

## Environment Variables Reference

| Variable | Description | Example |
|----------|-------------|---------|
| `GCP_PROJECT_ID` | GCP project identifier | `election-platform-2024` |
| `GCP_LOCATION` | Vertex AI and Firestore region | `asia-south1` |
| `ENVIRONMENT` | Deployment environment | `production` / `staging` / `development` |
| `CORS_ORIGINS` | Comma-separated allowed origins | `https://your-app.web.app` |
| `VERTEX_LLM_MODEL` | Vertex AI LLM model name | `gemini-1.5-flash-001` |
| `VERTEX_EMBEDDING_MODEL` | Vertex AI embedding model | `text-embedding-004` |
| `RATE_LIMIT_FAQ` | FAQ endpoint rate limit | `10/minute` |
| `RATE_LIMIT_TIMELINE` | Timeline endpoint rate limit | `30/minute` |

---

## Runtime Configuration (Cloud Run)

| Setting | Value | Rationale |
|---------|-------|-----------|
| Memory | 1024Mi | Sufficient for FastAPI + gRPC vector traffic |
| CPU | 1 | Scales linearly with instances |
| CPU Throttling | Enabled | CPU allocated only during requests (cost savings) |
| Min Instances | 0 | Zero cost during off-election periods |
| Max Instances | 100 | Caps runaway costs during spikes |
| Concurrency | 80 | Requests per container before scaling |

---

## Troubleshooting

### Common Issues

1. **Firestore permission denied**: Ensure IAM roles `roles/datastore.viewer` and `roles/datastore.user` are granted.
2. **Vertex AI quota error**: Check regional quotas for `text-embedding-004` and `gemini-1.5-flash-001`.
3. **Cold start latency**: First request after scale-to-zero may take 3-5 seconds. Set `min-instances=1` for production if needed.
4. **Vector search returns empty**: Ensure the Firestore vector index is created (Step 1.4) and documents are ingested (Step 3.3).
5. **Translation API errors**: Verify `cloudtranslate.user` role is granted and Translation API is enabled.
