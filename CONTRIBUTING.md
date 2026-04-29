# Contributing

Thank you for your interest in improving Indian Election Process Education Assistant.

This repository uses a custom Proprietary Non-Commercial License. By contributing, you agree that your contribution may be included in this repository under the same license.

## Development Setup

Install dependencies:

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -r requirements.txt

cd ../frontend
npm ci
```

On Windows PowerShell:

```powershell
cd backend
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt

cd ..\frontend
npm ci
```

## Run Locally

Backend:

```bash
cd backend
uvicorn main:app --host 0.0.0.0 --port 8080 --reload
```

Frontend:

```bash
cd frontend
npm run dev
```

## Required Checks

Run backend tests:

```bash
cd backend
python -m pytest tests/ -v
```

Build the frontend:

```bash
cd frontend
npm run build
```

## Pull Request Guidelines

- Keep changes focused on one topic.
- Update documentation when behavior, setup, APIs, or deployment steps change.
- Do not commit credentials, service account keys, `.env` files, generated caches, logs, or local session files.
- Use placeholders such as `YOUR_GCP_PROJECT_ID` instead of real deployment values.
- Do not add private Cloud Run URLs or secrets to documentation.
- Include screenshots when changing frontend UI.

## Documentation Style

- Write for beginners.
- Use explicit commands.
- Avoid vague instructions such as "configure accordingly".
- Document only features and commands that exist in the repository.
