# Security Policy

## Supported Versions

This repository currently tracks a single active version on the default branch.

## Reporting a Vulnerability

Please report security issues privately to the maintainer instead of opening a public GitHub issue.

Maintainer:

- Alok Ranjan Singh
- LinkedIn: https://www.linkedin.com/in/alokranjan-in/

Include:

- A clear description of the issue.
- Steps to reproduce.
- Affected files, endpoints, or workflows.
- Potential impact.
- Suggested fix, if known.

## Sensitive Data Rules

Do not commit:

- Google Cloud service account keys.
- `.env` files with real values.
- Firestore credentials.
- API keys.
- Access tokens.
- Private Cloud Run service URLs.
- Local session or tool state files.

The repository ignores `**/temp-key.json`, `.env`, virtual environments, `node_modules`, and `.codex`.

## Application Security Notes

The backend includes:

- CORS configuration from `CORS_ORIGINS`.
- Per-IP rate limiting with SlowAPI.
- Prompt-injection detection for FAQ input.
- Query length limits.
- PII detection and scrubbing for Aadhaar-like numbers, EPIC IDs, Indian phone numbers, and email addresses.

Google Cloud permissions should follow least privilege. Cloud Run service accounts need only the roles required for Firestore, Vertex AI, and Translation API access.
