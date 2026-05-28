from app.rag.retriever import retrieve

questions = [
    "What is Rakshitah?",
    "What is the value proposition of Rakshitah?",
    "What are the modules in Rakshitah?"
]

for question in questions:
    print("\n" + "=" * 50)
    print(f"Question: {question}")

    results = retrieve(question)

    for i, doc in enumerate(results, 1):
        print(f"\nResult {i}:")
        print(doc[:300])