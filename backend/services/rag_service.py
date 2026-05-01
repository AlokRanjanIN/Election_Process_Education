"""
RAG (Retrieval-Augmented Generation) pipeline service.

Orchestrates the flow between vector search and LLM generation.
"""

import json
import logging
from typing import List, Tuple
from google.cloud.firestore_v1.client import Client as FirestoreClient
from starlette.concurrency import run_in_threadpool

from core.config import settings
from models.faq import FAQResponse, Citation
from services.vector_store import vector_search, ContextDocument
from services.llm_provider import get_embedding, generate_answer

logger = logging.getLogger(__name__)

# --- Grounded system prompt template ---
SYSTEM_PROMPT = """You are the Indian Election Process Education Assistant. Your ONLY purpose is to provide accurate information about the Indian election process based on verified Election Commission of India (ECI) documents.

STRICT RULES:
1. You must formulate answers STRICTLY from the <context> blocks provided below.
2. If the answer cannot be found in the context, your ONLY valid response is: "I do not have verified ECI information on this topic."
3. Do NOT answer based on your internal knowledge.
4. Do NOT discuss politics, political parties, candidates, or election results.
5. Always cite your sources by referencing the document title from the context.

RESPONSE FORMAT:
Provide your answer in the following JSON format:
{
  "answer": "Your clear, grounded answer here",
  "citations": [
    {"title": "Source document title", "url": "Source URL"}
  ]
}"""

# --- Fallback responses ---
NO_CONTEXT_RESPONSE = FAQResponse(
    answer="I do not have verified ECI information on this topic.",
    citations=[
        Citation(title="Election Commission of India", url="https://eci.gov.in/"),
    ],
)

def build_grounded_prompt(query: str, context_docs: List[ContextDocument]) -> str:
    """Construct a grounded prompt with retrieved context."""
    context_blocks = []
    for i, doc in enumerate(context_docs, 1):
        context_blocks.append(
            f"<context id=\"{i}\" source=\"{doc.title}\" url=\"{doc.url}\">\n"
            f"{doc.content}\n"
            f"</context>"
        )

    context_str = "\n\n".join(context_blocks) if context_blocks else "No relevant documents found."

    return (
        f"{SYSTEM_PROMPT}\n\n"
        f"--- RETRIEVED ECI DOCUMENTS ---\n"
        f"{context_str}\n\n"
        f"--- USER QUESTION ---\n"
        f"{query}\n"
    )

def parse_llm_response(raw_response: str) -> Tuple[str, List[Citation]]:
    """Parse JSON response from LLM."""
    try:
        # Simple extraction logic for JSON blocks
        cleaned = raw_response.strip()
        if "```json" in cleaned:
            cleaned = cleaned.split("```json")[1].split("```")[0].strip()
        
        parsed = json.loads(cleaned)
        answer = parsed.get("answer", raw_response)
        citations = [
            Citation(title=c.get("title", "ECI Document"), url=c.get("url", "https://eci.gov.in/"))
            for c in parsed.get("citations", [])
        ]
        return answer, citations
    except Exception as e:
        logger.warning("LLM Response parsing failed: %s", e)
        return raw_response, []

async def ask_faq(db: FirestoreClient, query: str, locale: str = "en-IN") -> FAQResponse:
    """Full RAG pipeline: embed → search → prompt → LLM → parse."""
    try:
        # Step 1: Embed
        query_embedding = await run_in_threadpool(get_embedding, query)
        
        # Step 2: Search
        context_docs = await run_in_threadpool(vector_search, db, query_embedding, settings.RAG_TOP_K)
        if not context_docs:
            return NO_CONTEXT_RESPONSE

        # Step 3: Prompt & LLM
        prompt = build_grounded_prompt(query, context_docs)
        raw_response = await run_in_threadpool(generate_answer, prompt)

        # Step 4: Parse
        answer, citations = parse_llm_response(raw_response)
        
        # Ensure fallback citations if LLM missed them
        if not citations:
            citations = [Citation(title=d.title, url=d.url) for d in context_docs[:2]]

        return FAQResponse(answer=answer, citations=citations, locale=locale)

    except Exception as e:
        logger.exception("RAG pipeline error: %s", e)
        return NO_CONTEXT_RESPONSE
