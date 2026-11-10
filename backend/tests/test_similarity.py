from services.pdf_reader import extract_text
from services.chunker import create_chunks
from services.embeddings import model

from sentence_transformers import util

# Read PDF
pages = extract_text("uploads/machine_learning_5_pages.pdf")

# Split PDF into chunks
chunks = create_chunks(pages, chunk_size=200, overlap=40)

# Ask a question related to your PDF
query = "What are the different types of machine learning?"

# Convert question into vector
query_vector = model.encode(query, convert_to_tensor=True)

# Convert document chunks into vectors
chunk_vectors = model.encode(
    [chunk["content"] for chunk in chunks],
    convert_to_tensor=True
)

# Calculate cosine similarity
scores = util.cos_sim(query_vector, chunk_vectors)[0]

# Find the 3 most similar chunks
top_results = scores.argsort(descending=True)[:3]

print("\nTOP 3 RELEVANT CHUNKS\n")

for index in top_results:

    index = int(index)

    print("Similarity:", round(float(scores[index]), 4))
    print("Page:", chunks[index]["page_number"])
    print("Content:", chunks[index]["content"])
    print("-" * 50)