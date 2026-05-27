from langchain_community.document_loaders import PyPDFLoader
from langchain.text_splitter import RecursiveCharacterTextSplitter

from pathlib import Path
import uuid
import logging

from app.rag.chroma_client import get_collection
from app.rag.embeddings import get_embedding

logging.basicConfig(level=logging.INFO)

# -------------------------
# 1. Resolve PDF Path Safely
# -------------------------
BASE_DIR = Path(__file__).resolve().parent
pdf_path = (BASE_DIR / "../../docs/Rakshitah_GRC_WhitePaper 3 index pdf.pdf").resolve()

if not pdf_path.exists():
    raise FileNotFoundError(f"PDF not found at: {pdf_path}")

logging.info(f"Loading PDF from: {pdf_path}")

# -------------------------
# 2. Load PDF
# -------------------------
loader = PyPDFLoader(str(pdf_path))
documents = loader.load()

# -------------------------
# 3. Split into chunks
# -------------------------
splitter = RecursiveCharacterTextSplitter(
    chunk_size=500,
    chunk_overlap=50
)

chunks = splitter.split_documents(documents)

logging.info(f"Total chunks created: {len(chunks)}")

# -------------------------
# 4. Get Chroma Collection
# -------------------------
collection = get_collection()

# -------------------------
# 5. Add to Vector DB
# -------------------------
ids = []
texts = []
embeddings = []
metadatas = []

for i, chunk in enumerate(chunks):
    text = chunk.page_content.strip()
    if not text:
        continue

    embedding = get_embedding(text)

    doc_id = f"rag-{i}-{uuid.uuid4().hex}"

    ids.append(doc_id)
    texts.append(text)
    embeddings.append(embedding)
    metadatas.append({
        "source": str(pdf_path),
        "page": chunk.metadata.get("page", "N/A"),
        "section": "GRC Whitepaper"
    })

# Batch insert (better performance)
collection.add(
    ids=ids,
    documents=texts,
    embeddings=embeddings,
    metadatas=metadatas
)

logging.info(f"Stored {len(ids)} chunks in ChromaDB ✅")