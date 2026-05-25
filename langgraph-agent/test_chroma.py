from app.rag.chroma_client import get_collection

collection = get_collection()

print(collection.name)