import logging
from typing import List
from google.cloud.firestore_v1.client import Client as FirestoreClient
from google.cloud.firestore_v1.vector import Vector
from google.cloud.firestore_v1.base_vector_query import DistanceMeasure
from core.config import settings

logger = logging.getLogger(__name__)

class ContextDocument:
    def __init__(self, id: str, title: str, content: str, url: str):
        self.id = id
        self.title = title
        self.content = content
        self.url = url

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "url": self.url
        }

def vector_search(db: FirestoreClient, query_embedding: List[float], top_k: int = 3) -> List[ContextDocument]:
    """Execute nearest-neighbor vector search against Firestore."""
    collection_ref = db.collection(settings.COLLECTION_ECI_VECTOR_DOCS)

    vector_query = collection_ref.find_nearest(
        vector_field="embedding",
        query_vector=Vector(query_embedding),
        distance_measure=DistanceMeasure.COSINE,
        limit=top_k,
    )

    results: List[ContextDocument] = []
    for doc in vector_query.stream():
        data = doc.to_dict()
        results.append(ContextDocument(
            id=doc.id,
            title=data.get("title", "Unknown Document"),
            content=data.get("content", ""),
            url=data.get("url", "https://eci.gov.in/")
        ))

    logger.info("Vector search returned %d results.", len(results))
    return results
