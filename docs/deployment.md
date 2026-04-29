# Deployment

This project is designed for Google Cloud Run deployment with Docker containers.

Use placeholders in this guide:

| Placeholder | Replace with |
| --- | --- |
| `YOUR_GCP_PROJECT_ID` | Your Google Cloud project ID. |
| `YOUR_PROJECT_NUMBER` | Your Google Cloud project number. |
| `YOUR_SERVICE_ACCOUNT_EMAIL` | Service account used by Cloud Run or GitHub Actions. |
| `YOUR_BACKEND_CLOUD_RUN_URL` | URL of your deployed backend service. |
| `YOUR_FRONTEND_CLOUD_RUN_URL` | URL of your deployed frontend service. |

## Prerequisites

Install:

- Docker
- Google Cloud CLI
- Python 3.11 or newer
- Node.js 18 or newer

Authenticate:

```bash
gcloud auth login
gcloud config set project YOUR_GCP_PROJECT_ID
```

Enable APIs:

```bash
gcloud services enable run.googleapis.com
gcloud services enable firestore.googleapis.com
gcloud services enable aiplatform.googleapis.com
gcloud services enable translate.googleapis.com
gcloud services enable cloudbuild.googleapis.com
gcloud services enable artifactregistry.googleapis.com
```

## Firestore and Data Setup

Create Firestore:

```bash
gcloud firestore databases create --location=asia-south1 --type=firestore-native
```

Create the vector index:

```bash
gcloud firestore indexes composite create --collection-group=eci_vector_docs --query-scope=COLLECTION --field-config=vector-config='{"dimension":"768","flat": "{}"}',field-path=embedding
```

Seed data from your local machine:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
gcloud auth application-default login
export GCP_PROJECT_ID=YOUR_GCP_PROJECT_ID
export GCP_LOCATION=asia-south1
python -m scripts.seed_firestore
python -m scripts.ingest --data-file data/seed_eci_docs.json
```

Windows PowerShell:

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
gcloud auth application-default login
$env:GCP_PROJECT_ID = "YOUR_GCP_PROJECT_ID"
$env:GCP_LOCATION = "asia-south1"
python -m scripts.seed_firestore
python -m scripts.ingest --data-file data/seed_eci_docs.json
```

## IAM Permissions

Get the project number:

```bash
gcloud projects describe YOUR_GCP_PROJECT_ID --format="value(projectNumber)"
```

Set the service account email:

```bash
export SA_EMAIL=YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com
```

Grant required roles:

```bash
gcloud projects add-iam-policy-binding YOUR_GCP_PROJECT_ID --member="serviceAccount:${SA_EMAIL}" --role="roles/datastore.user"
gcloud projects add-iam-policy-binding YOUR_GCP_PROJECT_ID --member="serviceAccount:${SA_EMAIL}" --role="roles/aiplatform.user"
gcloud projects add-iam-policy-binding YOUR_GCP_PROJECT_ID --member="serviceAccount:${SA_EMAIL}" --role="roles/cloudtranslate.user"
```

Windows PowerShell:

```powershell
$env:SA_EMAIL = "YOUR_PROJECT_NUMBER-compute@developer.gserviceaccount.com"
gcloud projects add-iam-policy-binding YOUR_GCP_PROJECT_ID --member="serviceAccount:$env:SA_EMAIL" --role="roles/datastore.user"
gcloud projects add-iam-policy-binding YOUR_GCP_PROJECT_ID --member="serviceAccount:$env:SA_EMAIL" --role="roles/aiplatform.user"
gcloud projects add-iam-policy-binding YOUR_GCP_PROJECT_ID --member="serviceAccount:$env:SA_EMAIL" --role="roles/cloudtranslate.user"
```

## Backend Docker

Build locally:

```bash
cd backend
docker build -t election-api .
```

Run locally:

```bash
docker run --rm -p 8080:8080 -e GCP_PROJECT_ID=YOUR_GCP_PROJECT_ID -e GCP_LOCATION=asia-south1 -e ENVIRONMENT=production -e CORS_ORIGINS=http://localhost:5173 election-api
```

Verify:

```bash
curl http://localhost:8080/health
```

## Deploy Backend to Cloud Run

Build with Cloud Build:

```bash
cd backend
gcloud builds submit --tag gcr.io/YOUR_GCP_PROJECT_ID/election-api
```

Deploy:

```bash
gcloud run deploy election-api \
  --image gcr.io/YOUR_GCP_PROJECT_ID/election-api \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated \
  --memory 1024Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 100 \
  --concurrency 80 \
  --cpu-throttling \
  --set-env-vars GCP_PROJECT_ID=YOUR_GCP_PROJECT_ID,GCP_LOCATION=asia-south1,ENVIRONMENT=production,CORS_ORIGINS=YOUR_FRONTEND_CLOUD_RUN_URL
```

Get the backend URL:

```bash
gcloud run services describe election-api --platform managed --region asia-south1 --format="value(status.url)"
```

Verify:

```bash
curl YOUR_BACKEND_CLOUD_RUN_URL/health
```

## Frontend Docker

Build locally:

```bash
cd frontend
docker build --build-arg VITE_API_BASE_URL=YOUR_BACKEND_CLOUD_RUN_URL -t election-web .
```

Run locally:

```bash
docker run --rm -p 8082:8080 election-web
```

Open:

```text
http://localhost:8082
```

## Deploy Frontend to Cloud Run

Build with Cloud Build from the frontend directory:

```bash
cd frontend
gcloud builds submit --config cloudbuild.yaml --substitutions _VITE_API_BASE_URL=YOUR_BACKEND_CLOUD_RUN_URL
```

Deploy:

```bash
gcloud run deploy election-web \
  --image gcr.io/YOUR_GCP_PROJECT_ID/election-web \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated \
  --memory 512Mi \
  --cpu 1 \
  --min-instances 0 \
  --max-instances 20 \
  --port 8080
```

Get the frontend URL:

```bash
gcloud run services describe election-web --platform managed --region asia-south1 --format="value(status.url)"
```

After deployment, update backend CORS:

```bash
gcloud run services update election-api --region asia-south1 --set-env-vars GCP_PROJECT_ID=YOUR_GCP_PROJECT_ID,GCP_LOCATION=asia-south1,ENVIRONMENT=production,CORS_ORIGINS=YOUR_FRONTEND_CLOUD_RUN_URL
```

## Static Frontend Hosting Option

The frontend can also be hosted as static files after `npm run build`.

Build:

```bash
cd frontend
npm ci
VITE_API_BASE_URL=YOUR_BACKEND_CLOUD_RUN_URL npm run build
```

Create a Cloud Storage bucket:

```bash
gsutil mb -l asia-south1 gs://YOUR_GCP_PROJECT_ID-frontend
```

Upload build files:

```bash
gsutil -m rsync -r dist/ gs://YOUR_GCP_PROJECT_ID-frontend
```

Make objects public:

```bash
gsutil iam ch allUsers:objectViewer gs://YOUR_GCP_PROJECT_ID-frontend
```

Configure website serving:

```bash
gsutil web set -m index.html -e index.html gs://YOUR_GCP_PROJECT_ID-frontend
```

## GitHub Actions

The repository includes `.github/workflows/deploy.yml`.

Current workflow behavior:

| Trigger | Behavior |
| --- | --- |
| Pull request to `main` | Runs backend tests. |
| Push to `main` | Runs backend tests, builds backend Docker image, pushes it, and deploys `election-api` to Cloud Run. |

The workflow deploys the backend service only. It does not deploy the frontend.

Required GitHub secrets:

| Secret | Purpose |
| --- | --- |
| `GCP_PROJECT_ID` | Google Cloud project ID. |
| `WIF_PROVIDER` | Workload Identity Federation provider. |
| `WIF_SERVICE_ACCOUNT` | Service account used by GitHub Actions. |

Create a Workload Identity Pool:

```bash
gcloud iam workload-identity-pools create github-pool --location=global --display-name="GitHub Actions Pool"
```

Create an OIDC provider:

```bash
gcloud iam workload-identity-pools providers create-oidc github-provider \
  --location=global \
  --workload-identity-pool=github-pool \
  --display-name="GitHub Provider" \
  --attribute-mapping="google.subject=assertion.sub,attribute.repository=assertion.repository" \
  --issuer-uri="https://token.actions.githubusercontent.com"
```

## Production Verification

Backend health:

```bash
curl YOUR_BACKEND_CLOUD_RUN_URL/health
```

Backend API root:

```bash
curl YOUR_BACKEND_CLOUD_RUN_URL/
```

Eligibility endpoint:

```bash
curl -X POST YOUR_BACKEND_CLOUD_RUN_URL/api/v1/eligibility/evaluate \
  -H "Content-Type: application/json" \
  -d '{"dob":"2000-01-15","is_citizen":true,"state_of_residence":"MH","is_nri":false}'
```

Frontend:

```text
YOUR_FRONTEND_CLOUD_RUN_URL
```
