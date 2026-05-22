from app.rag.embeddings import get_embedding

vector = get_embedding("What is GRC?")

print(len(vector))