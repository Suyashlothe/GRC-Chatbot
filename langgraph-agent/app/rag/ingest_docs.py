from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from app.rag.chroma_client import get_collection
from app.rag.embeddings import get_embedding

pdf_path = "../data/documents/Rakshitah_GRC_WhitePaper 1.pdf"

loader = PyPDFLoader(pdf_path)
documents = loader.load()

splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = splitter.split_documents(documents)

collection = get_collection()

for i, chunk in enumerate(chunks):
    embedding = get_embedding(chunk.page_content)

    collection.add(
        ids=[str(i)],
        documents=[chunk.page_content],
        embeddings=[embedding]
    )

print(f"Stored {len(chunks)} chunks in ChromaDB")