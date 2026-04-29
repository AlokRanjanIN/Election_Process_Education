# Indian Election Process Education Assistant

Indian Election Process Education Assistant is a full-stack web application that helps users understand voter eligibility, registration steps, election timelines, and election-process FAQs for India.

The project contains:

- A **FastAPI backend** with rule-based voter eligibility checks, registration guide steps, timeline lookup, and an FAQ assistant.
- A **React + Vite frontend** with pages for eligibility, guide, timeline, and FAQ workflows.
- Google Cloud integrations for Firestore, Vertex AI, Translation API, Docker, Cloud Run, and GitHub Actions deployment.

## Features

| Feature | What it does |
| --- | --- |
| Voter eligibility checker | Evaluates age, citizenship, state code, and NRI status using deterministic backend rules. |
| Registration guide | Returns step-by-step voter registration instructions from a backend state machine. |
| Election timeline lookup | Reads constituency election events from Firestore by state code and optional constituency ID. |
| FAQ assistant | Uses security checks, optional translation, Firestore vector search, and Vertex AI to answer election-process questions. |
| Hindi and English frontend | Uses `i18next` and `react-i18next` for English and Hindi UI text. |
| API documentation | FastAPI serves OpenAPI JSON, Swagger UI, and ReDoc. |
| Docker support | Separate backend and frontend Dockerfiles are included. |
| Cloud Run deployment | The repository includes backend deployment automation for Google Cloud Run. |

## Tech Stack

| Area | Technology |
| --- | --- |
| Backend | Python, FastAPI, Uvicorn, Pydantic |
| Frontend | React, TypeScript, Vite, React Router, Axios |
| Styling | Tailwind CSS |
| Internationalization | i18next, react-i18next |
| Data | Google Cloud Firestore |
| AI services | Vertex AI text embeddings, Vertex AI Gemini model |
| Translation | Google Cloud Translation API |
| Security and limits | SlowAPI rate limiting, prompt-injection checks, PII scrubbing |
| Testing | Pytest, FastAPI TestClient |
| Deployment | Docker, Google Cloud Run, Cloud Build, GitHub Actions |

## Quick Start

These commands run the backend and frontend locally on a fresh machine after prerequisites are installed.

### 1. Clone the repository

```bash
git clone YOUR_REPOSITORY_URL
cd Election_Process_Education
```

### 2. Start the backend

Linux and macOS:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

Windows PowerShell:

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

Backend URLs:

- API root: <http://localhost:8080/>
- Health check: <http://localhost:8080/health>
- Swagger UI: <http://localhost:8080/docs>
- ReDoc: <http://localhost:8080/redoc>

### 3. Start the frontend

Open a second terminal.

```bash
cd frontend
npm ci
npm run dev
```

Frontend URL:

- Application: <http://localhost:5173>

The Vite development server proxies `/api` requests to `http://localhost:8080`.

## Detailed Documentation

| Document | Purpose |
| --- | --- |
| [Installation](docs/installation.md) | Install prerequisites on Linux, macOS, and Windows. |
| [Setup](docs/setup.md) | Configure environment variables, Google Cloud, Firestore, and seed data. |
| [Usage](docs/usage.md) | Run the backend, frontend, tests, and common workflows. |
| [API](docs/api.md) | Backend endpoints, request bodies, response bodies, and curl examples. |
| [Frontend](docs/frontend.md) | Frontend routes, folders, components, state, and API integration. |
| [Architecture](docs/architecture.md) | System design, data flow, and important backend/frontend modules. |
| [Troubleshooting](docs/troubleshooting.md) | Common setup, runtime, API, Docker, and deployment problems. |
| [Deployment](docs/deployment.md) | Docker, Cloud Run, Cloud Build, and GitHub Actions deployment. |
| [Privacy](docs/privacy.md) | Privacy-relevant data flow, PII handling, logging, and cloud service notes. |
| [Contributing](CONTRIBUTING.md) | Development setup, checks, PR rules, and documentation style. |
| [Security](SECURITY.md) | Vulnerability reporting and sensitive data rules. |
| [Support](SUPPORT.md) | Where to find help and what to include in bug reports. |
| [Changelog](CHANGELOG.md) | Notable repository changes. |

## Folder Structure

```text
Election_Process_Education/
├── backend/
│   ├── api/                 # FastAPI routers
│   ├── core/                # Config, Firebase, middleware, security helpers
│   ├── data/                # Seed JSON for timelines and ECI documents
│   ├── models/              # Pydantic request and response models
│   ├── scripts/             # Firestore seed and document ingestion scripts
│   ├── services/            # Business logic, Firestore access, RAG, translation
│   ├── tests/               # Pytest test suite
│   ├── Dockerfile
│   ├── main.py
│   └── requirements.txt
├── frontend/
│   ├── src/
│   │   ├── api/             # Axios API client and TypeScript types
│   │   ├── components/      # Page components
│   │   ├── locales/         # English and Hindi translations
│   │   ├── App.tsx
│   │   ├── i18n.ts
│   │   └── main.tsx
│   ├── Dockerfile
│   ├── cloudbuild.yaml
│   ├── nginx.conf
│   ├── package.json
│   └── vite.config.ts
├── docs/                    # Project documentation
├── .github/workflows/       # Backend Cloud Run deployment workflow
├── DEPLOYMENT.md            # Existing deployment notes
└── README.md
```

## Screenshots

### Home

![Home page showing the Election Guide India landing page and four workflow cards](screenshots/1_Home.png)

### Eligibility

![Eligibility page showing the voter eligibility form and eligible result](screenshots/2_Eligibility.png)

### Registration Guide

![Registration guide page showing step progress, instructions, useful links, and previous step navigation](screenshots/3_Guide.png)

### Timeline

![Election timeline page showing state selection and timeline results](screenshots/4_Timeline.png)

### FAQ

![Ask a Question page showing the FAQ input form and voice input button](screenshots/5_Ask.png)

## Verification Commands

Run backend tests:

```bash
cd backend
python -m pytest tests/ -v
```

Build the frontend:

```bash
cd frontend
npm ci
npm run build
```

## License

This repository is licensed under a custom **Proprietary Non-Commercial License**.

Commercial use, redistribution, sublicensing, and publication of modified versions are not allowed without prior written permission from the author. See [LICENSE](LICENSE) for details.

## Author

**Alok Ranjan Singh**

- LinkedIn: [linkedin.com/in/alokranjan-in](https://www.linkedin.com/in/alokranjan-in/)
