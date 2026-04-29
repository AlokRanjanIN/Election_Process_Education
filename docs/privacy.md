# Privacy

This document describes the privacy-relevant behavior implemented in this repository.

## Data Entered by Users

The frontend can send these user inputs to the backend:

| Page | Data sent |
| --- | --- |
| Eligibility | Date of birth, citizenship status, state code, and NRI status. |
| Guide | Current guide workflow state. |
| Timeline | State code and optional constituency ID. |
| FAQ | Question text and locale. |

## FAQ PII Handling

The FAQ endpoint applies PII detection and scrubbing before calling the FAQ retrieval pipeline.

The backend currently detects:

- Aadhaar-like 12-digit numbers.
- EPIC IDs matching three uppercase letters followed by seven digits.
- Indian phone numbers.
- Email addresses.

Detected values are replaced with redaction markers before the FAQ service is called.

## Logging

The backend logs request method, path, status code, and duration. The request logging middleware is designed not to log raw query payloads.

Some service-level log messages include limited metadata, such as state codes, locale, or shortened FAQ query text.

## Google Cloud Services

Depending on the workflow, the backend may use:

- Firestore for timeline and vector document storage.
- Vertex AI for FAQ embeddings and answer generation.
- Google Cloud Translation API for non-English FAQ translation.

Operators deploying this application are responsible for configuring Google Cloud IAM, data retention, and access controls for their environment.

## Credentials

Do not commit credentials to the repository.

Local development should use:

```bash
gcloud auth application-default login
```

Cloud Run should use service account permissions instead of JSON key files.
