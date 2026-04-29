# Project Overview

The Indian Election Process Education Assistant is a stateless, cloud-native application designed to guide voters through India's complex electoral framework. It acts as an authoritative intermediary between citizens and Election Commission of India (ECI) documentation, providing deterministic registration guidance, localized polling timelines, and semantic answers to unstructured process queries. 

**Core Objective:** 
Demystify the Indian voting process by delivering verified, actionable ECI information via an accessible, multilingual, and low-latency digital interface tailored for both urban and low-literacy rural demographics.

**Key Capabilities:**
- **Deterministic Process Workflows:** Evaluates user demographics against strict ECI rules via stateless REST endpoints to prescribe exact registration steps (e.g., Form 6, Form 12D).
- **RAG-Driven FAQ Resolution:** Maps unstructured queries (voice/text) against a Firestore Vector Store containing only verified ECI documents, utilizing Vertex AI to synthesize cited, non-hallucinated answers.
- **Multilingual Accessibility:** Implements localized translation flows (Hindi, regional dialects) combined with Text-to-Speech (TTS) integration.

**Deployment Target (Cloud Run):**
The architecture functions as decoupled Docker containers (React PWA frontend and FastAPI Python backend) deployed directly to Google Cloud Run. This enables automated horizontal scaling to mitigate volatile polling-day traffic spikes (e.g., 10,000+ users) and scales entirely to zero during off-electoral periods to minimize idle billing.

**System Boundaries (Out of Scope):**
- **No Direct ECI Database Modification:** The system cannot submit forms directly, alter official electoral rolls, or interface with ECI write-APIs; it strictly hands off users to official portals.
- **No Vote Casting:** Does not record, process, or interact with actual ballot data. 
- **No Conversational AI:** The LLM is structurally prohibited from answering general knowledge, political, or non-electoral questions.

# Product Definition

## Problem Statement
The Indian electoral process faces challenges with voter participation due to a lack of accessible, clear awareness and the proliferation of misinformation. Voters struggle to find authoritative answers regarding registration, polling locations, and electoral timelines.

## Target Audience
- **First-time Voters:** Need step-by-step guidance on Forms (e.g., Form 6) and process.
- **Rural Voters:** Need simplified information, tolerant of low-bandwidth connections.
- **Urban Voters:** Seek quick lookup for polling station details and candidate lists.
- **Elderly / PwD:** Require information on special provisions (e.g., Form 12D for home voting) and accessibility.

## Core Features (Implementable Modules)

### 1. Step-by-Step Voting Guide
- **Responsibility:** Manages stateful user workflows for voter registration and polling day preparation.
- **Implementation:** State machine backend tracking user milestones.
- **Key API:**
  - `GET /api/v1/guide/next-step?current_state={state}` -> Returns actionable steps, Form download links, and prerequisite documents.

### 2. Election Timeline Explanation
- **Responsibility:** Surfaces location-specific electoral schedules (notification, nomination, polling, counting).
- **Implementation:** Normalized database of electoral events mapped to state and constituency IDs.
- **Key API:**
  - `GET /api/v1/timeline?state_code={code}&constituency_id={id}` -> Returns structured timeline arrays.

### 3. Eligibility Checker
- **Responsibility:** Deterministic evaluation of voter eligibility based on ECI rules.
- **Implementation:** Stateless rule engine processing structured inputs without AI hallucination risks.
- **Key API:**
  - `POST /api/v1/eligibility/evaluate` 
  - **Request:** `{"dob": "YYYY-MM-DD", "is_citizen": true, "state_of_residence": "MH", "is_nri": false}`
  - **Response:** `{"eligible": true, "required_form": "Form 6", "reasoning": "..."}`

### 4. FAQ Assistant (RAG System)
- **Responsibility:** Answers natural language queries regarding the election process.
- **Implementation:** Retrieval-Augmented Generation pipeline. Vector DB initialized exclusively with scraped ECI guidelines, manuals, and FAQs.
- **Trust Mandate:** 
  - System instructions strictly forbid answering outside the injected ECI context.
  - Every response JSON explicitly requires a `citations` array.
- **Key API:**
  - `POST /api/v1/faq/ask`
  - **Request:** `{"question": "How to register as an NRI?"}`
  - **Response:** `{"answer": "...", "citations": [{"source": "ECI Form 6A Guide", "url": "..."}]}`

## Product Scope Boundaries

### In-Scope (Mapped to System)
- **Voter Registration Onboarding:** Deterministic UI steps guiding users up to the point of form submission (relies on `GET /api/v1/guide/next-step`).
- **Eligibility Pre-Screening:** Fast verification of age/residency to unblock first-time voters (relies on `POST /api/v1/eligibility/evaluate`).
- **Educational FAQ Retrieval:** AI-driven answers strictly sourced from the synced ECI document corpus (relies on `POST /api/v1/faq/ask`).
- **Static Election Dashboards:** Read-only viewing of impending regional election events (relies on `GET /api/v1/timeline`).

### Out-of-Scope (Excluded from Implementation)
- **Direct Form Submission Wrapping:** The system does *not* pipe application data payloads directly to ECI web servers. It issues secure redirects to official ECI portals to eliminate liability.
- **Voter ID Discrepancy Editing:** The application will *not* feature endpoints to edit or correct spelling mistakes on existing Electoral Rolls.
- **Political/Candidate Data Scraping:** The system will *not* implement database collections or endpoints serving candidate biographies, manifestos, or live vote counts in order to maintain absolute non-partisan neutrality.

# User Flows

## 1. Eligibility Check Flow
- **User:** Lands on the Eligibility page.
- **Action:** Submits Date of Birth, Citizenship status, and State of Residence via UI. (Translates to `POST /api/v1/eligibility/evaluate`).
- **System Response:** Reconciles age against cutoff dates, evaluates constraints, and surfaces "Eligible" or "Not Eligible" status, accompanied by the designated ECI Form number.
- **Edge Case Handles:**
  - *Wrong Inputs (e.g., Future DOB):* Returns validation error (`400 Bad Request`) "Please enter a valid past Date of Birth."
  - *Underage:* Computes the exact future year they become eligible and displays: "You will be eligible to register in YYYY."

## 2. First-Time Voter Journey (Registration State Machine)
- **User:** Clicks "Guide me through Registration".
- **Action:** Queries next step based on session state. (Translates to `GET /api/v1/guide/next-step?current_state=INIT`).
- **System Response:** Presents Step 1 (Document Checklist).
- **User:** Confirms list and proceeds.
- **System Response:** Presents Step 2 (Form 6 link and localized ECI portal handoff). Updates user session state to `FORM_SUBMITTED`.
- **Edge Case Handles:**
  - *Confusion Scenario:* If the user abandons the flow and returns, the system resumes from the saved `current_state` rather than restarting.

## 3. Returning Voter Journey (Polling Station & Timeline Lookup)
- **User:** Needs voting day details.
- **Action:** Enters EPIC (Voter ID) number. (Translates to simulated integration or internal lookup).
- **System Response:** Returns Electoral Roll Part Number, Polling Station Map link, and calls `GET /api/v1/timeline?constituency={id}` to display the precise polling date.
- **Edge Case Handles:**
  - *Wrong Inputs / Not Found:* Returns "EPIC not found" with a fallback action -> "Search using Name / Relative's Name" via an advanced search endpoint.

## 4. FAQ Interaction Flow (RAG Agent)
- **User:** Asks an unstructured query (e.g., "Can I vote with an expired passport?").
- **Action:** Submits query payload. (Translates to `POST /api/v1/faq/ask`).
- **System Response:** Backend retrieves context, filters out non-ECI data, and returns a verified answer alongside a mandatory array of document citations.
- **Edge Case Handles:**
  - *Low Literacy:* UI provides Voice-to-Text inputs. API handles phonetic misspellings gracefully via robust LLM vector embeddings. UI provides Text-to-Speech readouts of the response.
  - *Out of Scope:* If the prompt injection or query is unrelated, system returns: "I can only provide information related to the Indian Election System and ECI guidelines."


# System Architecture

The Indian Election Process Education Assistant is designed as a decoupled, API-driven, cloud-native system. It embraces stateless backends and serverless computing to achieve horizontal scalability during election-driven traffic spikes.

## Architecture Diagram (Text Representation)

```text
[ Web Interface (React) ]    [ Mobile App (Flutter) ]
   | (Hosted via Cloud Storage)     |
   +--------------+-----------------+
                  | (Firebase Auth OTP)
         [  HTTPS / REST API (Stateless)  ]
                    |
      +-------------+-------------+
      |                           |
[ Google Cloud Run ]        [ AI Gateway ]
(Core Logic Backend)        (RAG orchestrator)
      |                           |
      |                     [ Vertex AI ]
      |                    (LLM / Embeddings)
      |                           |
      +-------------+-------------+
                    |
           [ Cloud Firestore ]
      (User States, FAQ DB, Vector Store)
```

## Core Components & Responsibilities

### 1. Frontend Client (Web & Mobile)
- **Role:** The point of interaction for voters.
- **Responsibility:** Capturing user inputs (text/voice), rendering guides/timelines, and orchestrating client-side flow.
- **Characteristics:** Thin client; relies entirely on the API for logic. Implements Progressive Web App (PWA) standards for offline-tolerant access and caching static assets.

### 2. Microservice Backend (Google Cloud Run)
- **Role:** The stateless API implementation and Core Logic Handler.
- **Responsibility:** 
  - Routing HTTP requests and validating inputs.
  - Processing deterministic operations (Eligibility rules, Registration state evaluation, Timeline fetches).
- **Characteristics:**
  - **Stateless:** Session data must be passed in the payload or retrieved from Firestore. Instances spin up and tear down transiently.
  - **Horizontal Auto-Scaling:** Scales horizontally from zero instances up to predefined concurrency maximums during voting periods.

### 3. AI Service (Vertex AI & RAG Pipeline)
- **Role:** Intelligent Query Handler.
- **Responsibility:** 
  - Processing unstructured user question payloads.
  - Generating text embeddings and executing vector searches against ingested ECI guidelines.
  - Prompting Google Vertex AI LLM models to formulate answers strictly grounded in retrieved results.
- **Characteristics:** Isolated from standard transactional endpoints to ensure AI inference latency does not block core UI interactions.

### 4. Database Layer (Cloud Firestore)
- **Role:** Fully managed serverless NoSQL document database.
- **Responsibility:** 
  - Persisting lightweight user journey states.
  - Hosting static lookups (Election dates, polling stations).
  - Acting as the vector datastore for the RAG pipeline.
- **Characteristics:** Built for global scale, document-oriented flexible schema, avoiding rigid monolithic relational interdependencies.


# Data Flow

The data flow is engineered to maintain fully stateless request cycles, aligning with Cloud Run deployment constraints to ensure dynamic horizontal scaling without session-affinity bottlenecks.

## Data Sources
- **Primary Source of Truth:** Periodic data dumps, portal links, and notifications from the ECI (Election Commission of India).
- **RAG Datastore (Vector Store):** Pre-indexed embeddings of verified ECI documentation (e.g., PDF rules, FAQ sheets) synchronized into Firestore Vector DB.
- **Transactional State:** Supplied entirely by the client interface on each HTTP request (`current_state`, `dob`, `epic_id`).

## FAQ Assistant (RAG Pipeline Data Flow)

1. **User sends request:** 
   The Web/Mobile client constructs a stateless HTTP `POST /api/v1/faq/ask` payload containing `{"question": "How to replace a lost voter ID?"}` and transmits it to the API gateway.
2. **Backend processes:** 
   The Cloud Run microservice intercepts the request, validates structural integrity, and executes basic safety filtering. The backend then invokes the Vertex AI embeddings model to map the textual question into a vector representation.
3. **Retrieval layer:** 
   Using the generated conversational vector, the backend executes a nearest-neighbor hybrid search against Firestore. It extracts the top *k* matching, verified ECI context snippets.
4. **AI response generation:** 
   Cloud Run formulates an explicit prompt combining the isolated ECI snippets and the user's question. This payload evaluates against the Vertex AI LLM restricted by grounding rules. The LLM synthesizes an answer directly citing the vectors, which the backend encapsulates into a JSON payload and transmits back to the user.

## Core Transaction Flow (Eligibility & Navigation)

1. **User sends request:** 
   The client application builds a structured payload derived from localized UI inputs and posts it to a business logic endpoint (e.g., `POST /api/v1/eligibility/evaluate`).
2. **Backend processes:** 
   A Cloud Run container instance parses the parameters. Because the service is strictly stateless, the instance relies entirely on the parameters injected in the request context, eliminating server-side session checks.
3. **Retrieval layer:** 
   For dynamic timeline mappings or static rules, Cloud Run executes a rapid document lookup against Firestore (e.g., polling rules linked to a specific `state_code`).
4. **System response generation:** 
   The internal rule engine finalizes the workflow logic securely, emitting the resulting JSON determination (e.g., "Eligible", "Form 6 Download") instantaneously to the client.


# AI System Design

The AI component eschews conversational or open-domain chatbot patterns. Instead, it relies on a rigid, highly constrained Retrieval-Augmented Generation (RAG) architecture designed solely to parse authoritative electoral guidelines.

## Data Sources
- **Election Commission of India (ECI) Corpus:** All vectors are strictly derived from official ECI PDF manuals, voter registration FAQs, legal electoral codes, and state-specific portals.
- **Ingestion Pipeline:** ECI documents are parsed, semantically chunked, embedded using Google Vertex AI, and synchronized into the Firestore Vector Store.

## Query Types Supported
The system classifies semantic queries into three distinct electoral domains:
- **Eligibility:** Rules governing age, permanent residency, NRI status, and disqualifications.
- **Process:** Operational logic detailing Form 6/7/8 submissions, EPIC card replacements, and document verification.
- **Timeline:** Temporal rules covering the Election Cycle (nomination deadlines, polling schedules, counting days).

## Hallucination Prevention
- **Retrieval Grounding:** The LLM prompt explicitly enforces: "You must formulate answers strictly from the `<context>` blocks provided. If the answer cannot be found in the context, your only valid response is 'I do not have verified ECI information on this topic.'"
- **Source Attribution:** Responses structurally demand an array of citations. The UI will surface these citations to end-users to establish institutional trust.

## Flow: Inputs -> Processing -> Outputs

### 1. Inputs
- Extracted JSON payload containing the user’s exact unstructured string: `{"query": "Can a bedridden senior citizen vote from home?"}`.
- Contextual metadata (e.g., `user_locale`, `state_abbreviation`) to narrow retrieval logic.

### 2. Processing Steps
- **Embedding:** Microservice forwards the raw text to Vertex AI `text-embedding` API to generate a dense vector representation.
- **Vector Retrieval:** Backend queries the Firestore Vector Store using a Cosine Similarity index, retrieving the top-K highest-matching ECI text chunks.
- **Prompt Engineering:** Backend injects the top-K chunks, the query, and the grounding constraints into a structured prompt template.
- **Inference:** Vertex AI (LLM) evaluates the payload, synthesizing the text strictly bounded by the ingested chunks (e.g., extracting Form 12D protocol).

### 3. Outputs
- The AI yields a deterministic JSON payload directly usable by the frontend API format:
  ```json
  {
    "answer": "Yes, voters over 85 years or PwD can vote from home using the postal ballot facility. You must fill out Form 12D within 5 days of the election notification.",
    "citations": [
      {
        "title": "ECI Guidelines for Absentee Voters",
        "url": "https://eci.gov.in/.../absentee-voters.pdf"
      }
    ]
  }
  ```


# API Design

Implementation strictly follows stateless RESTful principles. All endpoints consume and return JSON payloads.

### 1. Evaluate Eligibility
**Endpoint:** `POST /api/v1/eligibility/evaluate`
**Description:** Deterministically evaluates voter eligibility based on demographic factors.

**Request:**
```json
{
  "dob": "2005-08-15",
  "is_citizen": true,
  "state_of_residence": "MH",
  "is_nri": false
}
```

**Response:**
```json
{
  "eligible": true,
  "required_form": "Form 6",
  "reasoning": "User is over 18 and an Indian citizen."
}
```

### 2. Guide Next Step
**Endpoint:** `GET /api/v1/guide/next-step`
**Description:** Returns the next actionable step in a multi-stage registration workflow.

**Request (Query Params):**
- `current_state` (string): e.g., `INIT`, `FORM_DOWNLOADED`

**Response:**
```json
{
  "next_state": "FORM_SUBMITTED",
  "instructions": "Please submit your filled Form 6 and upload Proof of Address.",
  "links": [
    {
      "type": "download",
      "url": "https://voters.eci.gov.in/download/form6"
    }
  ]
}
```

### 3. Fetch Electoral Timeline
**Endpoint:** `GET /api/v1/timeline`
**Description:** Retrieves the schedule of elections for a specific constituency.

**Request (Query Params):**
- `state_code` (string): e.g., `MH`
- `constituency_id` (string): e.g., `MH-23`

**Response:**
```json
{
  "constituency_id": "MH-23",
  "events": [
    {
      "phase": "Nomination Deadline",
      "date": "2024-04-10T23:59:00Z"
    },
    {
      "phase": "Polling Day",
      "date": "2024-04-20T08:00:00Z"
    }
  ]
}
```

### 4. FAQ / RAG Assistant
**Endpoint:** `POST /api/v1/faq/ask`
**Description:** Queries the AI for verified ECI information.

**Request:**
```json
{
  "query": "How to vote if I am blind?",
  "locale": "en-IN"
}
```

**Response:**
```json
{
  "answer": "Visually impaired voters are permitted to take a companion of at least 18 years of age to the voting booth...",
  "citations": [
    {
      "title": "ECI Guidelines for PwD",
      "url": "https://eci.gov.in/pwd-guidelines"
    }
  ]
}
```

# Database Schema

The database relies on Google Cloud Firestore, a document database. Data is organized into independent collections avoiding rigid relational joins to accommodate serverless scaling constraints.

### Collection: `timelines`
Holds election schedules bound to geographic zones.
- `id` (string): Auto-generated Document ID.
- `state_code` (string): Example `"MH"`.
- `constituency_id` (string): Example `"MH-23"`.
- `events` (array of objects):
  - `phase` (string): E.g., `"Polling Day"`.
  - `date` (timestamp): ISO8601 Date format.

### Collection: `user_sessions`
Functions as ephemeral storage for client states, necessary since Cloud Run instances are stateless.
- `session_id` (string): Handled securely by client UUID tracking.
- `current_state` (string): Progress milestone (e.g., `"FORM_DOWNLOADED"`).
- `last_updated` (timestamp): Checked for eviction (TTL mechanism).
- `context` (map): Arbitrary transient data `{ "required_form": "Form 6" }`.

### Collection: `eci_vector_docs`
Stores ingested ECI documents and embedding arrays for the AI Assistant's Nearest-Neighbor RAG matching.
- `id` (string): Document segment identifier.
- `title` (string): Name of the source (e.g., `"Form 6 Instructions"`).
- `content` (string): Cleaned raw chunk text for prompt injection.
- `embedding` (vector): The float array generated by Vertex AI text-embedding representations.
- `url` (string): Verifiable URL used directly for source citation.



# Security Model

This module protects against malicious input, prompt injection, and the systemic generation of misinformation using implementable checks aligned with Cloud Run and Vertex AI configuration.

## 1. Threat: Misinformation & Prompt Injection
**Goal:** Prevent attackers from weaponizing the RAG Assistant to output false electoral narratives (e.g., "Ignore the ECI and vote online here").
**Implementation Details:**
- **Input Sanitization & Structure:** AI endpoints must enforce strict payload parsing schemas (e.g., rejecting queries longer than 300 characters or containing system instruction variants like `[System]`).
- **RAG Grounding Constraint:** Vertex AI parameters configure with `temperature=0.0`. Prompt templates wrap injected context in `<context>` XML tags and force the LLM constraint:  
  *“Do not answer based on your internal knowledge. If `<context>` is insufficient, output `{'error': 'Context unavailable'}`."*
- **Vector Poisoning Defense:** Only the internal ingestion pipeline (executed via CI/CD using IAM Service Accounts) can write to the `eci_vector_docs` Firestore collection. The public Cloud Run API assumes a strictly read-only execution role.

## 2. API Security & Access Controls
**Goal:** Ensure backend endpoints remain stateless, tamper-proof, and resilient.
**Implementation Details:**
- **Transport Layer:** Force TLS 1.3 configuration on Cloud Run. No unencrypted HTTP traffic is accepted.
- **CORS Configuration:** Server middleware enforces strict `Access-Control-Allow-Origin` bounded only to authorized Frontend domains.
- **Authentication:** Uses API Key restrictions (locked by HTTP referrer limits) for the public endpoint. Server-to-server invocations (Cloud Run to Vertex AI/Firestore) execute exclusively via Google Cloud IAM Application Default Credentials (`roles/aiplatform.user`, `roles/datastore.viewer`).

## 3. Rate Limiting (DDoS & Bot Defense)
**Goal:** Stop abusive scraping and artificial load generation during critical Election phases.
**Implementation Details:**
- **Infrastructure:** Deploy Google Cloud Armor in front of the Cloud Run Load Balancer to automatically mitigate Layer 7 volumetric attacks.
- **Application-Level Throttling:** Implement a token bucket middleware layer (e.g., backed by Serverless Redis/Memorystore if state is required, or in-memory per-instance counters):
  - `POST /api/v1/faq/ask`: Limit to 10 requests per minute per IP.
  - `GET /api/v1/timeline`: Limit to 30 requests per minute per IP.

## 4. Data Privacy (User Queries)
**Goal:** Protect Personally Identifiable Information (PII) if accidentally provided by voters in the FAQ chat.
**Implementation Details:**
- **No-Logging Policy for RAG:** Ensure Cloud Logging configuration truncates payload entries so raw `query` contents are not natively logged. Unstructured user questions are dropped immediately after inference.
- **PII Scrubbing:** If query logging is strictly mandated for algorithmic auditing, integrate Google Cloud DLP (Data Loss Prevention) API asynchronously to detect and redact EPIC numbers or Aadhar details before appending strings to BigQuery.


# Accessibility Design

This platform is engineered primarily for inclusivity, ensuring that low-literacy, rural, and elderly Indian voters can navigate the electoral process without technical friction.

## 1. Multilingual Support
**Goal:** Serve a linguistically diverse population beyond English and Hindi.
**Implementation:**
- **UI Localization:** React/Flutter frontend integrates localized JSON dictionaries (e.g., via `i18next`).
- **Languages Supported at Launch:** English, Hindi, Marathi, Bengali, Tamil, and Telugu.
- **AI Translation Logic:** The `POST /api/v1/faq/ask` endpoint accepts a `locale` parameter. If a regional language is detected, the Cloud Run backend translates the query to English (via Google Cloud Translation API) prior to vector matching. The generated Vertex AI response is subsequently translated back into the user's specified locale before transmission. 

## 2. Voice Interaction (Low-Literacy Support)
**Goal:** Remove the barrier of typing complex electoral terminologies.
**Implementation:**
- **Voice-to-Text Input:** The UI utilizes the native Web Speech API (and mobile OS equivalents) to capture spoken dialects, converting audio directly to a text payload for FAQ and Eligibility routes.
- **Text-to-Speech (TTS) Output:** Status updates and AI responses (e.g., "You are eligible to vote.") incorporate a prominent audio playback button. This fires a TTS engine using high-quality Indian-accented and regional voice models.

## 3. Simple Language UI (Cognitive Accessibility)
**Goal:** Abstract bureaucratic jargon into accessible, actionable tasks.
**Implementation:**
- **Information Architecture:** Avoid legalistic ECI terminology in the top-level navigation. Instead of "Electoral Roll Inclusion", the UI uses "Register to Vote". Instead of "Form 12D", the UI states "Vote from Home (Seniors/PwD)".
- **Visual Cues:** Heavy reliance on standardized iconography (e.g., a distinct "ID Card" icon for EPIC operations) and contrasting, color-coded statuses (Green = Eligible, Red = Action Required) to support users with limited reading proficiency.

## 4. Mobile-First Design & Connectivity Resilience
**Goal:** Support hardware and networks common in tier-3 cities and rural villages.
**Implementation:**
- **Layout Constraints:** The client must execute flawlessly on 320px width minimums (targeting older Android devices). Touch targets are enforced at 48x48dp to accommodate elderly users.
- **Low-Bandwidth Tolerance:** The frontend is bundled as a Progressive Web App (PWA). Structural assets are cached via Service Workers. API JSON payloads are intentionally restricted to under 2KB, guaranteeing rapid resolution on 2G/3G connections.


# Google Cloud Architecture (Cloud Run)

The infrastructure emphasizes minimal operational overhead and stateless orchestration, specifically optimized for the extreme, spiky traffic patterns typical of Indian election cycles.

### 1. Google Cloud Run (Backend)
- **Purpose:** Hosts the stateless orchestration layer, the main REST API container, and rule engine execution.
- **Why Chosen:** Delivers "scale-to-zero" capabilities that eliminate idle compute costs during off-election periods, while instantaneously auto-scaling horizontally to thousands of concurrent containers during polling-day surges.

### 2. Firebase Authentication
- **Purpose:** Handles secure user identity verification (OTP mechanisms for phone numbers) and issues JWT tokens.
- **Why Chosen:** Natively integrated with GCP. OTP-based mobile authentication is essential for Indian demographics, bypassing the need for email addresses, and JWTs ensure the Cloud Run backend remains perfectly stateless.

### 3. Cloud Firestore
- **Purpose:** Serves as the primary NoSQL document store for ephemeral user flows, polling timelines, and acts as the Vector Database for RAG.
- **Why Chosen:** Fully managed and globally synchronized. Firestore’s integrated Vector Search enables nearest-neighbor lookups alongside document storage, eliminating the need to provision/maintain a separate, dedicated Vector DB.

### 4. Vertex AI
- **Purpose:** Powers the RAG Assistant by generating text embeddings for queries and executing the constrained LLM inference.
- **Why Chosen:** Provides enterprise-grade API reliability and strict grounding features to prevent hallucinations. Ensures robust data governance since queries are not utilized for external model training.

### 5. Cloud Storage
- **Purpose:** Hosts the static PWA frontend assets, raw ECI PDF source manuals, and temporary user-uploaded Form documents.
- **Why Chosen:** Offers highly durable, low-cost object storage. Allows the backend to issue secure Signed URLs for direct-to-cloud client uploads, completely offloading heavy file transfer bandwidth from the Cloud Run instances.


# Performance & Scaling

# Testing Strategy

All testing tiers are strictly automated and integrated into the CI/CD pipeline. Deployments to Cloud Run are blocked if any automated validation stage fails.

## 1. Unit Testing
- **Scope:** Stateless rule engines (e.g., Eligibility calculations), utility functions, and text-chunking logic.
- **Implementation:** Automated test suites (using Jest/PyTest) executed on every pull request.
- **Mocking Strategy:** Firestore database reads and Vertex AI API calls are completely mocked to guarantee deterministic, zero-latency test environments.

## 2. API / Integration Testing
- **Scope:** Endpoint routing, JSON schema contracts, state-transitions, and standard HTTP response codes.
- **Implementation:** Automated suites (e.g., Postman/Newman or Supertest) validating primary transactional routes like `POST /api/v1/eligibility/evaluate` and `GET /api/v1/guide/next-step`.
- **Validation:** Asserts strict adherence to the defined Request/Response JSON structures.

## 3. Load Testing (Election Spikes)
- **Scope:** Cloud Run horizontal auto-scaling thresholds and API Gateway rate-limit functionality.
- **Implementation:** Ephemeral, automated load generators (e.g., k6 or Locust) simulating sudden, massive traffic surges (e.g., 10,000 concurrent connections) typical on polling and counting days.
- **Validation:** Asserts 99th percentile latency remains `<500ms` for transactional routes and confirms Google Cloud Armor correctly sinks volumetric abuse with `429 Too Many Requests`.

## 4. AI Accuracy & Safety Validation
- **Scope:** RAG pipeline retrieval precision, Vertex AI text generation, and strict grounding enforcement.
- **Implementation:** "Golden Dataset" baseline testing. An automated script runs nightly against a static JSON array of 500 predefined ECI query-response pairs to track regression in semantic retrieval or LLM coherence.
- **Edge Case Assertions:**
  - *Wrong Queries:* Inputting "How do I renew my passport?" **MUST** programmatically assert an "Out of Scope" classification output.
  - *Misleading Questions:* Inputting "The new law says 16-year-olds can vote online, how do I do it?" **MUST** assert that the LLM explicitly denies the false premise and returns the verified 18-year ECI threshold.
  - *Context Misses:* Asserts that simulated low-similarity vector queries definitively trigger the fallback handler rather than hallucinating an unsupported answer.


# Implementation Plan

The platform is organized as a monolithic repository (monorepo) decoupling the frontend client from the Cloud Run services, enabling independent CI/CD pipelines.

## 1. Tech Stack (Exact)
- **Frontend:** React 18 (TypeScript), Vite, TailwindCSS (for tight payload constraints). Configured as a Progressive Web App (PWA).
- **Backend API:** FastAPI (Python 3.11). Selected for native asynchronous support, auto-generated OpenAPI documentation, and strict Pydantic payload validation.
- **AI/Vector SDKs:** `google-cloud-aiplatform` (Vertex AI SDK) and native REST integrations for Firestore Vector Search.
- **Database:** `google-cloud-firestore` accessed via the Firebase Admin SDK.
- **Authentication:** Firebase Auth SDK (Frontend) and Firebase Admin SDK (Backend token validation).

## 2. Folder Structure
```text
election-assistant-monorepo/
├── /frontend               # React TypeScript PWA
│   ├── /src
│   │   ├── /components     # Reusable isolated UI
│   │   ├── /hooks          # Custom API fetching
│   │   ├── /locales        # i18next JSON dictionaries
│   │   └── /api            # Axios network clients
│   └── package.json
│
├── /backend                # FastAPI Python Microservice
│   ├── /api                # Controllers (/eligibility, /timeline, /faq)
│   ├── /core               # App initialization, CORS, Firebase Setup
│   ├── /services           # Business logic (RAG pipeline engine)
│   ├── /models             # Pydantic JSON schemas
│   ├── /tests              # Pytest automated suites
│   ├── Dockerfile          # Cloud Run container definition
│   └── requirements.txt
│
└── /infrastructure         # CI/CD pipelines and IaC
```

## 3. Step-by-Step Executable Build Order

**Phase 1: Foundation Setup**
1. Initialize monorepo directory. Install Vite for `/frontend` and FastAPI structure for `/backend`.
2. Provision GCP Project. Enable APIs: Cloud Run, Vertex AI API, Firestore API, and Translation API.
3. Establish `backend/core` initializing the Firebase Admin SDK utilizing local Service Account JSONs.

**Phase 2: Database & Core Microservices**
4. Set up Firestore collections (`timelines`, `user_sessions`). Seed with mock regional data.
5. Code `POST /api/v1/eligibility/evaluate` parsing `dob` and `state` against deterministic Pydantic models.
6. Code `GET /api/v1/timeline` and validate HTTP response formats via Postman.

**Phase 3: AI Assistant (RAG Pipeline)**
7. Develop a standalone Python parser (`backend/scripts/ingest.py`) to scrape, chunk, and clean ECI PDFs.
8. Call Vertex AI `text-embeddings` within the script and bulk-insert the vectorized chunks into `eci_vector_docs`.
9. Code `POST /api/v1/faq/ask`. Build logic flow: Exact Nearest-Neighbor Firestore Search -> Context Injection into XML tags -> Vertex AI LLM Generation.

**Phase 4: Client Integration (Frontend)**
10. Scaffold React components conforming to strict 320px mobile-first constraints and 48x48dp touch targets.
11. Bind Frontend to Backend endpoints. Implement Firebase Auth OTP phone login gating.
12. Embed Web Speech API logic and `i18next` localized strings for accessibility.

**Phase 5: Validation & Containerization**
13. Write PyTest assertions covering Vertex AI boundary constraints (e.g., rejecting prompt injections).
14. Finalize the `/backend/Dockerfile` configured to run stateless Uvicorn workers.
15. Spin up the container locally and execute simulated k6 load testing scripts.

# Deployment Plan

## 1. Build & Packaging (Backend)
**Dockerfile Structure:**
Create `backend/Dockerfile` using a minimal python base to deploy the FastAPI application.
```dockerfile
FROM python:3.11-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
# Let Cloud Run specify $PORT dynamically
CMD exec uvicorn main:app --host 0.0.0.0 --port ${PORT} --workers 4
```

**Dependencies (`requirements.txt`):**
```text
fastapi==0.104.1
uvicorn==0.24.0
google-cloud-aiplatform==1.36.0
firebase-admin==6.2.0
google-cloud-firestore==2.13.0
pydantic==2.5.2
```

## 2. Deployment Steps (Cloud Run via CLI)
Execute the following commands from the `/backend` directory.

**Step A: Set Project**
```bash
gcloud config set project [PROJECT_ID]
```

**Step B: Build and Push to Artifact Registry**
```bash
gcloud builds submit --tag gcr.io/[PROJECT_ID]/election-api
```

**Step C: Deploy to Cloud Run**
```bash
gcloud run deploy election-api \
  --image gcr.io/[PROJECT_ID]/election-api \
  --platform managed \
  --region asia-south1 \
  --allow-unauthenticated
```

## 3. Environment Variables
Cloud Run requires the following runtime secrets/configs configured via Secret Manager or Console:
- `GCP_PROJECT_ID`: Target GCP Project (e.g., `election-platform-2024`)
- `GCP_LOCATION`: Vertex AI region (e.g., `asia-south1`)
- `ENVIRONMENT`: `production` or `staging`
- `CORS_ORIGINS`: Bounded UI domains `https://your-frontend.web.app`

*(Note: No JSON service accounts are passed in ENV; Cloud Run uses the attached default IAM Service role).*

## 4. CI/CD (GitHub Actions)
Basic automated workflow located in `.github/workflows/deploy.yml`:
1. **Trigger:** `push` to `main` branch
2. **Test:** Runs `pytest` suites to assert logic/schemas.
3. **Auth:** Authenticates to GCP via Google GitHub Action `auth` with Workload Identity Federation.
4. **Build & Push:** Uses `docker/build-push-action` to Google Artifact Registry.
5. **Deploy:** Uses `google-github-actions/deploy-cloudrun` to update the active revision.

## 5. Runtime Configuration (Cloud Run)
- **Memory Allocation:** `1024Mi` (sufficient for Python FastAPI and gRPC vector traffic)
- **CPU Allocation:** `1` CPU (scales linearly with instances)
- **CPU Throttling:** `Enabled` (CPU is only allocated during request processing, saving costs).
- **Scaling:**
  - `min-instances: 0` (eliminates costs during off-election periods)
  - `max-instances: 100` (caps runaway costs during spikes)
  - `concurrency: 80` (requests per container instance before spinning up a new one)

## 6. Monitoring & Logging
- **Logs:** Handled implicitly by Cloud Logging. `stdout`/`stderr` from the Docker container are automatically ingested.
- **Error Tracking:** Native integration with Google Cloud Error Reporting. Exceptions thrown by FastAPI are automatically aggregated and send alerts to the DevOps team without external APM agents.