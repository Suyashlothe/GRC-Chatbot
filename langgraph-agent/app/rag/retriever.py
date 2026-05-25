from app.rag.chroma_client import get_collection
from app.rag.embeddings import get_embedding


def retrieve(query: str, n_results: int = 3):
    collection = get_collection()

    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results
    )

    return results["documents"][0]