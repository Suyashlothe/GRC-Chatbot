from app.rag.chroma_client import get_collection
from app.rag.embeddings import get_embedding


def retrieve(query: str, n_results: int = 3):
    collection = get_collection()

    query_embedding = get_embedding(query)

    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=n_results,
    )

    documents = results["documents"][0]
    metadatas = results["metadatas"][0]

    final_results = []

    for doc, meta in zip(documents, metadatas):
        final_results.append({
            "text": doc,
            "source": meta.get("source", "unknown"),
            "page": meta.get("page", "N/A"),
            "section": meta.get("section", "N/A"),
        })

    return final_results