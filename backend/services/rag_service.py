"""
RAG (Retrieval-Augmented Generation) pipeline service.

Implements the AI System Design from plan.md:
  1. Embed user query via Vertex AI text-embedding
  2. Vector search against Firestore eci_vector_docs collection
  3. Construct grounded prompt with <context> XML tags
  4. LLM inference via Vertex AI with temperature=0.0
  5. Return answer + mandatory citations array

Hallucination Prevention:
  - LLM prompt enforces strict grounding to retrieved context
  - temperature=0.0 for deterministic outputs
  - Fallback response if context is insufficient

NOTE: Google Cloud SDK imports are deferred to function call time
to allow tests to run without GCP dependencies installed.
"""

import json
import logging
from typing import List, Tuple, TypedDict

from starlette.concurrency import run_in_threadpool

from core.config import settings
from models.faq import FAQResponse, Citation

logger = logging.getLogger(__name__)

# --- Vertex AI initialization flag ---
_vertex_initialized: bool = False
_embedding_model = None
_generative_model = None


class ContextDocument(TypedDict):
    """Retrieved ECI document used for grounded answer generation."""

    id: str
    title: str
    content: str
    url: str

# --- Grounded system prompt template ---
SYSTEM_PROMPT = """You are the Indian Election Process Education Assistant. Your ONLY purpose is to provide accurate information about the Indian election process based on verified Election Commission of India (ECI) documents.

STRICT RULES:
1. You must formulate answers STRICTLY from the <context> blocks provided below.
2. If the answer cannot be found in the context, your ONLY valid response is: "I do not have verified ECI information on this topic."
3. Do NOT answer based on your internal knowledge.
4. Do NOT discuss politics, political parties, candidates, or election results.
5. Do NOT provide any information unrelated to the Indian election process.
6. Always cite your sources by referencing the document title from the context.
7. Keep your answers clear, concise, and accessible to voters of all literacy levels.
8. If asked about voting procedures for PwD (Persons with Disabilities) or elderly voters, provide all available accommodations from the context.

RESPONSE FORMAT:
Provide your answer in the following JSON format:
{
  "answer": "Your clear, grounded answer here",
  "citations": [
    {"title": "Source document title", "url": "Source URL"}
  ]
}"""

# --- Out of scope response ---
OUT_OF_SCOPE_RESPONSE = FAQResponse(
    answer="I can only provide information related to the Indian Election System and ECI guidelines. "
    "Your question appears to be outside the scope of electoral processes. "
    "Please ask a question about voter registration, eligibility, polling procedures, or election timelines.",
    citations=[],
)

# --- Fallback when context is insufficient ---
NO_CONTEXT_RESPONSE = FAQResponse(
    answer="I do not have verified ECI information on this topic. "
    "For detailed information, please visit the official Election Commission of India website "
    "or contact the Voter Helpline at 1950.",
    citations=[
        Citation(
            title="Election Commission of India - Official Website",
            url="https://eci.gov.in/",
        ),
        Citation(
            title="National Voters' Service Portal",
            url="https://voters.eci.gov.in/",
        ),
    ],
)


def _ensure_vertex_initialized() -> None:
    """Initialize Vertex AI SDK (idempotent)."""
    global _vertex_initialized
    if not _vertex_initialized:
        from google.cloud import aiplatform

        aiplatform.init(
            project=settings.GCP_PROJECT_ID,
            location=settings.GCP_LOCATION,
        )
        _vertex_initialized = True
        logger.info(
            "Vertex AI initialized: project=%s, location=%s",
            settings.GCP_PROJECT_ID,
            settings.GCP_LOCATION,
        )


def generate_embedding(text: str) -> List[float]:
    """
    Generate a text embedding using Vertex AI text-embedding model.

    Args:
        text: Input text to embed.

    Returns:
        List of floats representing the embedding vector.
    """
    _ensure_vertex_initialized()

    global _embedding_model

    if _embedding_model is None:
        from vertexai.language_models import TextEmbeddingModel

        _embedding_model = TextEmbeddingModel.from_pretrained(
            settings.VERTEX_EMBEDDING_MODEL
        )

    embeddings = _embedding_model.get_embeddings([text])

    if not embeddings:
        logger.error("Empty embedding returned for text: %s", text[:50])
        return []

    return embeddings[0].values


def vector_search_firestore(
    query_embedding: List[float],
    top_k: int | None = None,
) -> List[ContextDocument]:
    """
    Execute nearest-neighbor vector search against Firestore eci_vector_docs.

    Uses Firestore's native vector search capability.

    Args:
        query_embedding: The query vector to search against.
        top_k: Number of top results to return.

    Returns:
        List of matching document dicts with title, content, url, and score.
    """
    if top_k is None:
        top_k = settings.RAG_TOP_K

    from core.firebase import get_firestore_client

    db = get_firestore_client()
    collection_ref = db.collection(settings.COLLECTION_ECI_VECTOR_DOCS)

    # Use Firestore vector search (find_nearest)
    from google.cloud.firestore_v1.vector import Vector
    from google.cloud.firestore_v1.base_vector_query import DistanceMeasure

    vector_query = collection_ref.find_nearest(
        vector_field="embedding",
        query_vector=Vector(query_embedding),
        distance_measure=DistanceMeasure.COSINE,
        limit=top_k,
    )

    results: List[ContextDocument] = []
    for doc in vector_query.stream():
        data = doc.to_dict()
        results.append({
            "id": doc.id,
            "title": data.get("title", "Unknown Document"),
            "content": data.get("content", ""),
            "url": data.get("url", "https://eci.gov.in/"),
        })

    logger.info("Vector search returned %d results.", len(results))
    return results


def build_grounded_prompt(query: str, context_docs: List[ContextDocument]) -> str:
    """
    Construct a grounded prompt with retrieved context wrapped in <context> XML tags.

    This is the core hallucination prevention mechanism described in plan.md.
    """
    context_blocks = []
    for i, doc in enumerate(context_docs, 1):
        context_blocks.append(
            f"<context id=\"{i}\" source=\"{doc['title']}\" url=\"{doc['url']}\">\n"
            f"{doc['content']}\n"
            f"</context>"
        )

    context_str = "\n\n".join(context_blocks) if context_blocks else "<context>No relevant documents found.</context>"

    prompt = (
        f"{SYSTEM_PROMPT}\n\n"
        f"--- RETRIEVED ECI DOCUMENTS ---\n"
        f"{context_str}\n\n"
        f"--- USER QUESTION ---\n"
        f"{query}\n\n"
        f"Provide your answer in the specified JSON format. "
        f"Remember: ONLY use information from the <context> blocks above."
    )

    return prompt


def invoke_llm(prompt: str) -> str:
    """
    Invoke Vertex AI LLM for grounded answer generation.

    Uses temperature=0.0 for deterministic outputs as specified in plan.md.
    """
    _ensure_vertex_initialized()

    global _generative_model

    from vertexai.generative_models import GenerationConfig

    if _generative_model is None:
        from vertexai.generative_models import GenerativeModel

        _generative_model = GenerativeModel(settings.VERTEX_LLM_MODEL)

    generation_config = GenerationConfig(
        temperature=settings.VERTEX_LLM_TEMPERATURE,
        max_output_tokens=1024,
        top_p=0.8,
        top_k=40,
    )

    response = _generative_model.generate_content(
        prompt,
        generation_config=generation_config,
    )

    return response.text


def parse_llm_response(raw_response: str) -> Tuple[str, List[Citation]]:
    """
    Parse the LLM's JSON response into answer + citations.

    Falls back to raw text if JSON parsing fails.
    """
    # Try to extract JSON from the response
    try:
        # Handle markdown code blocks in response
        cleaned = raw_response.strip()
        if cleaned.startswith("```json"):
            cleaned = cleaned[7:]
        if cleaned.startswith("```"):
            cleaned = cleaned[3:]
        if cleaned.endswith("```"):
            cleaned = cleaned[:-3]
        cleaned = cleaned.strip()

        parsed = json.loads(cleaned)
        answer = parsed.get("answer", raw_response)
        citations_data = parsed.get("citations", [])
        citations = [
            Citation(
                title=c.get("title", "ECI Document"),
                url=c.get("url", "https://eci.gov.in/"),
            )
            for c in citations_data
        ]
        return answer, citations
    except (json.JSONDecodeError, KeyError, TypeError) as e:
        logger.warning("Failed to parse LLM JSON response: %s", e)
        return raw_response, []


async def ask_faq(query: str, locale: str = "en-IN") -> FAQResponse:
    """
    Full RAG pipeline: embed → search → prompt → LLM → parse.

    Args:
        query: The user's natural language question.
        locale: Response locale (translation handled by caller).

    Returns:
        FAQResponse with grounded answer and citations.
    """
    logger.info("RAG pipeline invoked: locale=%s", locale)

    try:
        # Step 1: Generate query embedding
        query_embedding = await run_in_threadpool(generate_embedding, query)
        if not query_embedding:
            logger.error("Failed to generate embedding for query.")
            return NO_CONTEXT_RESPONSE

        # Step 2: Vector search against Firestore
        context_docs = await run_in_threadpool(vector_search_firestore, query_embedding)

        # Step 3: Check if we have relevant context
        if not context_docs:
            logger.info("No relevant context found for query.")
            return NO_CONTEXT_RESPONSE

        # Step 4: Build grounded prompt
        prompt = build_grounded_prompt(query, context_docs)

        # Step 5: Invoke LLM
        raw_response = await run_in_threadpool(invoke_llm, prompt)

        # Step 6: Parse response
        answer, citations = parse_llm_response(raw_response)

        # If no citations were extracted from LLM, build them from context docs
        if not citations:
            citations = [
                Citation(title=doc["title"], url=doc["url"])
                for doc in context_docs[:3]
            ]

        return FAQResponse(
            answer=answer,
            citations=citations,
            locale=locale,
        )

    except Exception as e:
        logger.exception("RAG pipeline error: %s", e)
        return FAQResponse(
            answer="An error occurred while processing your question. "
            "Please try again later or visit the official ECI website.",
            citations=[
                Citation(
                    title="Election Commission of India",
                    url="https://eci.gov.in/",
                )
            ],
            locale=locale,
        )
