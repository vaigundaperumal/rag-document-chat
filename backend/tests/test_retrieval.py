import os
import time

from dotenv import load_dotenv
from pinecone import Pinecone, DenseVectorQuery

from services.embeddings import model

load_dotenv()

# Connect to Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.index("rag-document-chat")

# User's question
query = "What are the different types of machine learning?"

# Convert question into an embedding
query_vector = model.encode(query).tolist()

# Search Pinecone
response = None

for attempt in range(5):

    response = index.documents.search(
        namespace="rag-documents",
        top_k=3,
        score_by=[
            DenseVectorQuery(
                field="embedding",
                values=query_vector
            )
        ],
        include_fields=["content", "page_number", "filename"]
    )

    if response.matches:
        break

    time.sleep(2)

# Display results
print("\nTOP 3 RELEVANT CHUNKS\n")

for result in response.matches:

    print("Score:", round(result.score, 4))
    print("Page:", result.page_number)
    print("Content:", result.content)
    print("-" * 60)