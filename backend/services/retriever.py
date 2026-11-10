
import os
import time

from dotenv import load_dotenv
from pinecone import Pinecone, DenseVectorQuery

from services.embeddings import model

load_dotenv()

pc = Pinecone(
    api_key=os.getenv("PINECONE_API_KEY")
)

index = pc.index("rag-document-chat")


def retrieve_chunks(question, namespace):

    # Convert question into embedding
    query_vector = model.encode(question).tolist()

    response = None

    # Search Pinecone
    for attempt in range(5):

        response = index.documents.search(
            namespace=namespace,
            top_k=3,
            score_by=[
                DenseVectorQuery(
                    field="embedding",
                    values=query_vector
                )
            ],
            include_fields=[
                "content",
                "page_number",
                "filename"
            ]
        )

        if response.matches:
            break

        time.sleep(2)

    # Extract retrieved chunks
    retrieved_chunks = []

    if response and response.matches:

        for result in response.matches:

            retrieved_chunks.append({
                "content": result.content,
                "page_number": result.page_number,
                "filename": result.filename
            })

    return retrieved_chunks
