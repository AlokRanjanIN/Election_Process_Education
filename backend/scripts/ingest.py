"""
ECI Document Ingestion Pipeline.

Implements plan.md Phase 3 Step 7-8:
  - Parses ECI documents (JSON seed data or PDF chunks)
  - Generates embeddings via Vertex AI text-embedding model
  - Bulk-inserts vectorized chunks into Firestore `eci_vector_docs` collection

Usage:
  python -m scripts.ingest --data-file data/seed_eci_docs.json
  python -m scripts.ingest --data-file data/seed_eci_docs.json --dry-run
"""

import argparse
import json
import logging
import sys
import os
import time

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from core.config import settings

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
)
logger = logging.getLogger(__name__)


def load_documents(data_file: str) -> list[dict]:
    """Load ECI documents from a JSON file."""
    logger.info("Loading documents from: %s", data_file)
    with open(data_file, "r", encoding="utf-8") as f:
        docs = json.load(f)
    logger.info("Loaded %d documents.", len(docs))
    return docs


def chunk_text(text: str, max_chunk_size: int = 1000, overlap: int = 200) -> list[str]:
    """
    Split long text into overlapping chunks for embedding.

    Args:
        text: Input text to chunk.
        max_chunk_size: Maximum characters per chunk.
        overlap: Number of overlapping characters between chunks.

    Returns:
        List of text chunks.
    """
    if len(text) <= max_chunk_size:
        return [text]

    chunks = []
    start = 0
    while start < len(text):
        end = start + max_chunk_size
        chunk = text[start:end]

        # Try to break at sentence boundary
        if end < len(text):
            last_period = chunk.rfind(".")
            last_semicolon = chunk.rfind(";")
            break_point = max(last_period, last_semicolon)
            if break_point > max_chunk_size // 2:
                chunk = chunk[: break_point + 1]
                end = start + break_point + 1

        chunks.append(chunk.strip())
        start = end - overlap

    return chunks


def generate_embeddings_batch(texts: list[str]) -> list[list[float]]:
    """
    Generate embeddings for a batch of texts using Vertex AI.

    Args:
        texts: List of text strings to embed.

    Returns:
        List of embedding vectors.
    """
    from google.cloud import aiplatform
    from vertexai.language_models import TextEmbeddingModel

    aiplatform.init(
        project=settings.GCP_PROJECT_ID,
        location=settings.GCP_LOCATION,
    )

    model = TextEmbeddingModel.from_pretrained(settings.VERTEX_EMBEDDING_MODEL)

    embeddings = []
    # Process in batches of 5 to avoid rate limits
    batch_size = 5
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        logger.info(
            "Generating embeddings: batch %d/%d (%d texts)",
            i // batch_size + 1,
            (len(texts) + batch_size - 1) // batch_size,
            len(batch),
        )
        batch_embeddings = model.get_embeddings(batch)
        embeddings.extend([e.values for e in batch_embeddings])

        # Rate limit pause
        if i + batch_size < len(texts):
            time.sleep(1)

    return embeddings


def upload_to_firestore(documents: list[dict], dry_run: bool = False) -> int:
    """
    Upload vectorized documents to Firestore eci_vector_docs collection.

    Args:
        documents: List of dicts with title, content, embedding, url fields.
        dry_run: If True, only log what would be uploaded.

    Returns:
        Number of documents uploaded.
    """
    if dry_run:
        logger.info("DRY RUN — Would upload %d documents.", len(documents))
        for doc in documents:
            logger.info(
                "  [DRY RUN] title='%s', content_len=%d, embedding_dim=%d",
                doc["title"],
                len(doc["content"]),
                len(doc.get("embedding", [])),
            )
        return len(documents)

    import firebase_admin
    from firebase_admin import credentials, firestore
    from google.cloud.firestore_v1.vector import Vector

    # Initialize Firebase
    if not firebase_admin._apps:
        cred = credentials.ApplicationDefault()
        firebase_admin.initialize_app(cred, {"projectId": settings.GCP_PROJECT_ID})

    db = firestore.client()
    collection_ref = db.collection(settings.COLLECTION_ECI_VECTOR_DOCS)

    count = 0
    for doc in documents:
        doc_data = {
            "title": doc["title"],
            "content": doc["content"],
            "url": doc["url"],
            "embedding": Vector(doc["embedding"]),
        }
        # Use title-based ID for idempotent uploads
        doc_id = doc["title"].lower().replace(" ", "_").replace("-", "_")[:100]
        collection_ref.document(doc_id).set(doc_data)
        count += 1
        logger.info("Uploaded: '%s' (id=%s)", doc["title"], doc_id)

    logger.info("Successfully uploaded %d documents to Firestore.", count)
    return count


def run_ingestion(data_file: str, dry_run: bool = False) -> None:
    """
    Execute the full ingestion pipeline.

    Steps:
      1. Load documents from JSON
      2. Chunk long texts
      3. Generate embeddings via Vertex AI
      4. Upload to Firestore eci_vector_docs
    """
    # Step 1: Load documents
    raw_docs = load_documents(data_file)

    # Step 2: Chunk and prepare
    prepared_docs = []
    for doc in raw_docs:
        chunks = chunk_text(doc["content"])
        for i, chunk in enumerate(chunks):
            prepared_docs.append({
                "title": doc["title"] + (f" (Part {i + 1})" if len(chunks) > 1 else ""),
                "content": chunk,
                "url": doc.get("url", "https://eci.gov.in/"),
            })

    logger.info(
        "Prepared %d chunks from %d documents.",
        len(prepared_docs),
        len(raw_docs),
    )

    if dry_run:
        logger.info("DRY RUN — Skipping embedding generation.")
        for doc in prepared_docs:
            doc["embedding"] = [0.0] * 768  # Placeholder
        upload_to_firestore(prepared_docs, dry_run=True)
        return

    # Step 3: Generate embeddings
    texts = [doc["content"] for doc in prepared_docs]
    embeddings = generate_embeddings_batch(texts)

    for doc, embedding in zip(prepared_docs, embeddings):
        doc["embedding"] = embedding

    # Step 4: Upload to Firestore
    upload_to_firestore(prepared_docs)

    logger.info("Ingestion pipeline complete.")


def main():
    parser = argparse.ArgumentParser(
        description="ECI Document Ingestion Pipeline — "
        "embed and upload ECI documents to Firestore Vector Store."
    )
    parser.add_argument(
        "--data-file",
        type=str,
        default="data/seed_eci_docs.json",
        help="Path to the JSON file containing ECI documents.",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Run without uploading to Firestore or generating embeddings.",
    )

    args = parser.parse_args()

    if not os.path.exists(args.data_file):
        logger.error("Data file not found: %s", args.data_file)
        sys.exit(1)

    run_ingestion(args.data_file, dry_run=args.dry_run)


if __name__ == "__main__":
    main()
