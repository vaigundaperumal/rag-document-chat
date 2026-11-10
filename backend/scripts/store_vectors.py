import os

from dotenv import load_dotenv
from pinecone import Pinecone

from services.pdf_reader import extract_text
from services.chunker import create_chunks
from services.embeddings import generate_embeddings

load_dotenv()

# Connect to Pinecone
api_key = os.getenv("PINECONE_API_KEY")

if not api_key:
    raise ValueError("Pinecone API key not found!")

pc = Pinecone(api_key=api_key)

# Connect to our existing index
index = pc.index("rag-document-chat")

# Read PDF
pages = extract_text("uploads/machine_learning_5_pages.pdf")

# Create chunks
chunks = create_chunks(
    pages,
    chunk_size=200,
    overlap=40
)

print("Total chunks:", len(chunks))

if not chunks:
    raise ValueError("No text chunks found!")

# Generate embeddings
vectors = generate_embeddings(chunks)

print("Total embeddings:", len(vectors))

# Prepare Pinecone records
documents = []

for i, (chunk, vector) in enumerate(zip(chunks, vectors)):

    documents.append({
        "_id": f"research-pdf-chunk-{i + 1}",
        "embedding": vector,
        "content": chunk["content"],
        "page_number": chunk["page_number"],
        "filename": "machine_learning_5_pages.pdf"
    })

# Upload to Pinecone
response = index.documents.upsert(
    namespace="rag-documents",
    documents=documents
)

print("Successfully uploaded:", response.upserted_count)