# API

The backend is a FastAPI application defined in `backend/main.py`.

Local base URL:

```text
http://localhost:8080
```

Production examples should replace `YOUR_BACKEND_CLOUD_RUN_URL` with your deployed backend URL.

## Authentication

The API routes in this codebase do not require user authentication.

Google Cloud authentication is required only for backend server access to Firestore, Vertex AI, and Translation API.

## Rate Limits

The backend uses SlowAPI with in-memory per-IP rate limiting.

| Endpoint | Default limit |
| --- | --- |
| `POST /api/v1/faq/ask` | `10/minute` |
| `GET /api/v1/timeline` | `30/minute` |
| Other endpoints | `60/minute` |

## Error Shapes

The custom 404 handler returns:

```json
{
  "error": "not_found",
  "message": "The requested resource '/path' was not found."
}
```

The rate-limit handler returns:

```json
{
  "error": "rate_limit_exceeded",
  "message": "Too many requests. Please try again later.",
  "retry_after_seconds": 60
}
```

FastAPI validation errors may return a `detail` field.

## System: API Root

```http
GET /
```

Example:

```bash
curl http://localhost:8080/
```

Response:

```json
{
  "service": "Indian Election Process Education Assistant",
  "version": "1.0.0",
  "documentation": "/docs",
  "health": "/health",
  "endpoints": {
    "eligibility": "POST /api/v1/eligibility/evaluate",
    "guide": "GET /api/v1/guide/next-step",
    "timeline": "GET /api/v1/timeline",
    "faq": "POST /api/v1/faq/ask"
  }
}
```

## System: Health Check

```http
GET /health
```

Example:

```bash
curl http://localhost:8080/health
```

Response:

```json
{
  "status": "healthy",
  "environment": "development",
  "version": "1.0.0"
}
```

## API Documentation Endpoints

| Endpoint | Purpose |
| --- | --- |
| `GET /docs` | Swagger UI. |
| `GET /redoc` | ReDoc UI. |
| `GET /openapi.json` | OpenAPI JSON document. |

## Eligibility: Evaluate Voter Eligibility

```http
POST /api/v1/eligibility/evaluate
```

This endpoint uses deterministic backend rules. It does not call AI services.

### Request Body

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `dob` | string | Yes | Date in `YYYY-MM-DD` format. Must be in the past. |
| `is_citizen` | boolean | Yes | Whether the user is an Indian citizen. |
| `state_of_residence` | string | Yes | Two-letter Indian state or union territory code. |
| `is_nri` | boolean | No | Defaults to `false`. |

Example:

```bash
curl -X POST http://localhost:8080/api/v1/eligibility/evaluate \
  -H "Content-Type: application/json" \
  -d '{"dob":"2000-01-15","is_citizen":true,"state_of_residence":"MH","is_nri":false}'
```

Response:

```json
{
  "eligible": true,
  "required_form": "Form 6",
  "reasoning": "You are eligible to vote. Please register using Form 6 in the state of MH.",
  "eligible_from_year": null
}
```

Possible `required_form` values from the current implementation:

| Condition | Form |
| --- | --- |
| Domestic eligible voter | `Form 6` |
| Eligible NRI voter | `Form 6A` |
| Ineligible user | `null` |

## Guide: Get Next Registration Step

```http
GET /api/v1/guide/next-step
```

### Query Parameters

| Parameter | Required | Default | Notes |
| --- | --- | --- | --- |
| `current_state` | No | `INIT` | Current registration workflow state. |

Valid states:

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

Example:

```bash
curl "http://localhost:8080/api/v1/guide/next-step?current_state=INIT"
```

Response shape:

```json
{
  "current_state": "INIT",
  "next_state": "DOCUMENTS_CHECKLIST",
  "instructions": "Welcome to the voter registration process!...",
  "links": [
    {
      "type": "info",
      "url": "https://voters.eci.gov.in/",
      "label": "National Voters' Service Portal"
    }
  ],
  "step_number": 1,
  "total_steps": 7
}
```

## Timeline: Fetch Electoral Timeline

```http
GET /api/v1/timeline
```

This endpoint reads from the Firestore `timelines` collection.

### Query Parameters

| Parameter | Required | Notes |
| --- | --- | --- |
| `state_code` | Yes | Two-letter Indian state or union territory code. |
| `constituency_id` | No | Constituency identifier such as `MH-23`. |

Example:

```bash
curl "http://localhost:8080/api/v1/timeline?state_code=MH&constituency_id=MH-23"
```

Response:

```json
[
  {
    "constituency_id": "MH-23",
    "events": [
      {
        "phase": "Election Notification",
        "date": "2024-03-20T10:00:00Z"
      },
      {
        "phase": "Polling Day",
        "date": "2024-04-20T07:00:00Z"
      }
    ]
  }
]
```

If no timeline data exists for the query, the endpoint returns `404`.

## FAQ: Ask the FAQ Assistant

```http
POST /api/v1/faq/ask
```

This endpoint performs input sanitization, length validation, prompt-injection detection, PII scrubbing, optional translation, Firestore vector search, Vertex AI generation, and response parsing.

### Request Body

| Field | Type | Required | Notes |
| --- | --- | --- | --- |
| `query` | string | Yes | 3 to 300 characters. |
| `locale` | string | No | Defaults to `en-IN`. Unsupported locales fall back to `en-IN`. |

Supported locales in the backend:

```text
en-IN
hi-IN
mr-IN
bn-IN
ta-IN
te-IN
```

Example:

```bash
curl -X POST http://localhost:8080/api/v1/faq/ask \
  -H "Content-Type: application/json" \
  -d '{"query":"How do I register as a new voter?","locale":"en-IN"}'
```

Response shape:

```json
{
  "answer": "Answer text from the FAQ assistant.",
  "citations": [
    {
      "title": "Source document title",
      "url": "https://example.com/source"
    }
  ],
  "locale": "en-IN"
}
```

Prompt-injection attempts return a blocked answer with status `200`.

## Production Curl Pattern

Replace `YOUR_BACKEND_CLOUD_RUN_URL` with your deployed backend URL:

```bash
curl YOUR_BACKEND_CLOUD_RUN_URL/health
```
