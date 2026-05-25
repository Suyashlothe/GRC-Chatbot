from app.rag.retriever import retrieve

results = retrieve("What is Rakshitha?")

for i, doc in enumerate(results, 1):
    print(f"\nResult {i}:")
    print(doc[:500])