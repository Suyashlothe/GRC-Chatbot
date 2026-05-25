import chromadb

client = chromadb.PersistentClient(path="./data/chroma")

def get_collection():
    return client.get_or_create_collection(
        name="grc_documents"
    )