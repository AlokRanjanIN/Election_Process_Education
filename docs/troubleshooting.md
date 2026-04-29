# Troubleshooting

This guide lists common errors and exact fixes.

## `pytest: command not found`

Cause: Backend dependencies are not installed or the virtual environment is not active.

Linux and macOS:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m pytest tests/ -v
```

Windows PowerShell:

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python -m pytest tests/ -v
```

## `tsc: not found`

Cause: Frontend dependencies are not installed.

Fix:

```bash
cd frontend
npm ci
npm run build
```

## `npm ci` Fails

Cause: Node.js or npm is missing, or the wrong Node.js version is installed.

Check versions:

```bash
node --version
npm --version
```

Install Node.js 18 or newer, then retry:

```bash
cd frontend
npm ci
```

## Backend Port Already in Use

Error examples:

```text
Address already in use
Errno 98
```

Run the backend on another port:

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8081 --reload
```

If you change the backend port, update the Vite proxy in `frontend/vite.config.ts` before using the local frontend proxy.

## Frontend Port Already in Use

Run Vite on another port:

```bash
cd frontend
npm run dev -- --port 5174
```

If the backend CORS settings do not include the new frontend origin, set:

```bash
export CORS_ORIGINS=http://localhost:5174
```

Windows PowerShell:

```powershell
$env:CORS_ORIGINS = "http://localhost:5174"
```

Restart the backend after changing `CORS_ORIGINS`.

## CORS Error in Browser

Cause: The backend does not allow the frontend origin.

Fix for local development:

```bash
cd backend
export CORS_ORIGINS=http://localhost:5173,http://localhost:3000
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

Windows PowerShell:

```powershell
cd backend
$env:CORS_ORIGINS = "http://localhost:5173,http://localhost:3000"
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

Fix for production:

```bash
gcloud run services update election-api --region asia-south1 --set-env-vars CORS_ORIGINS=YOUR_FRONTEND_CLOUD_RUN_URL
```

## Firestore Permission Denied

Cause: The local user or Cloud Run service account does not have Firestore permissions.

For local development:

```bash
gcloud auth application-default login
gcloud config set project YOUR_GCP_PROJECT_ID
```

For Cloud Run, grant Firestore access to the service account:

```bash
gcloud projects add-iam-policy-binding YOUR_GCP_PROJECT_ID --member="serviceAccount:YOUR_SERVICE_ACCOUNT_EMAIL" --role="roles/datastore.user"
```

## Firestore Database Not Found

Cause: Firestore native database has not been created.

Fix:

```bash
gcloud firestore databases create --location=asia-south1 --type=firestore-native
```

## Timeline Endpoint Returns 404

Cause: The `timelines` collection has no matching documents.

Seed timeline data:

```bash
cd backend
python -m scripts.seed_firestore
```

Test with a seeded state and constituency:

```bash
curl "http://localhost:8080/api/v1/timeline?state_code=MH&constituency_id=MH-23"
```

## FAQ Endpoint Returns Fallback Answer

Cause: The FAQ vector collection is empty, Vertex AI is unavailable, or vector search did not return context.

Run document ingestion:

```bash
cd backend
python -m scripts.ingest --data-file data/seed_eci_docs.json
```

Check required APIs:

```bash
gcloud services list --enabled --filter="name:(aiplatform.googleapis.com OR firestore.googleapis.com OR translate.googleapis.com)"
```

## Firestore Vector Search Error

Cause: The vector index for `eci_vector_docs.embedding` may be missing.

Create the index:

```bash
gcloud firestore indexes composite create --collection-group=eci_vector_docs --query-scope=COLLECTION --field-config=vector-config='{"dimension":"768","flat": "{}"}',field-path=embedding
```

## Translation API Error

Cause: Translation API is disabled or the service account lacks permission.

Enable the API:

```bash
gcloud services enable translate.googleapis.com
```

Grant permission:

```bash
gcloud projects add-iam-policy-binding YOUR_GCP_PROJECT_ID --member="serviceAccount:YOUR_SERVICE_ACCOUNT_EMAIL" --role="roles/cloudtranslate.user"
```

## Vertex AI Error

Cause: Vertex AI API is disabled, the region is wrong, or the service account lacks permission.

Enable the API:

```bash
gcloud services enable aiplatform.googleapis.com
```

Grant permission:

```bash
gcloud projects add-iam-policy-binding YOUR_GCP_PROJECT_ID --member="serviceAccount:YOUR_SERVICE_ACCOUNT_EMAIL" --role="roles/aiplatform.user"
```

Use the configured region:

```bash
export GCP_LOCATION=asia-south1
```

Windows PowerShell:

```powershell
$env:GCP_LOCATION = "asia-south1"
```

## Docker Build Fails for Backend

Build from the backend directory:

```bash
cd backend
docker build -t election-api .
```

Do not build the backend Dockerfile from the repository root unless you pass the correct build context.

## Docker Build Fails for Frontend

Build from the frontend directory:

```bash
cd frontend
docker build -t election-web .
```

## Frontend Cannot Reach Backend in Production

Cause: The production frontend was built without the correct `VITE_API_BASE_URL`.

Rebuild with the backend URL:

```bash
cd frontend
docker build --build-arg VITE_API_BASE_URL=YOUR_BACKEND_CLOUD_RUN_URL -t election-web .
```

## Browser Voice Input Does Not Work

Cause: `FAQPage` uses the Web Speech API. Not every browser supports `SpeechRecognition`.

Fix:

1. Use a Chromium-based browser.
2. Allow microphone permission.
3. Type the question manually if voice input is unavailable.
