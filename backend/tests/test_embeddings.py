from services.pdf_reader import extract_text
from services.chunker import create_chunks
from services.embeddings import generate_embeddings


pdf_path = "uploads/machine_learning_5_pages.pdf"

# Extract text
pages = extract_text(pdf_path)

# Create chunks
chunks = create_chunks(
    pages,
    chunk_size=200,
    overlap=40
)

print("Total chunks:", len(chunks))

# Generate embeddings
vectors = generate_embeddings(chunks)

print("Total vectors:", len(vectors))

# Check first vector
print("First vector dimensions:", len(vectors[0]))

print("First 5 values:", vectors[0][:5])