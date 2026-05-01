import logging
from typing import List
from core.config import settings

logger = logging.getLogger(__name__)

_vertex_initialized: bool = False
_embedding_model = None
_generative_model = None

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

def get_embedding(text: str) -> List[float]:
    """Generate a text embedding using Vertex AI."""
    _ensure_vertex_initialized()
    global _embedding_model
    if _embedding_model is None:
        from vertexai.language_models import TextEmbeddingModel
        _embedding_model = TextEmbeddingModel.from_pretrained(settings.VERTEX_EMBEDDING_MODEL)
    
    embeddings = _embedding_model.get_embeddings([text])
    return embeddings[0].values if embeddings else []

def generate_answer(prompt: str) -> str:
    """Invoke Vertex AI LLM for grounded answer generation."""
    _ensure_vertex_initialized()
    global _generative_model
    from vertexai.generative_models import GenerationConfig, GenerativeModel
    
    if _generative_model is None:
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
