
import os
import time

from dotenv import load_dotenv
from pinecone import Pinecone, DenseVectorQuery

from services.embeddings import model
from services.prompt_builder import build_prompt
from services.llm import generate_answer

load_dotenv()

# Connect to Pinecone
pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))
index = pc.index("rag-document-chat")


def retrieve_chunks(question):

    # Convert question into embedding
    query_vector = model.encode(question).tolist()

    response = None

    # Retry retrieval if no results are returned
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

    # Convert Pinecone results into dictionaries
    retrieved_chunks = []

    if response and response.matches:

        for result in response.matches:

            retrieved_chunks.append({
                "content": result.content,
                "page_number": result.page_number,
                "filename": result.filename
            })

    return retrieved_chunks


def rag_pipeline(question):

    print("\nSearching documents...")

    # Step 1: Retrieve relevant chunks
    retrieved_chunks = retrieve_chunks(question)

    if not retrieved_chunks:
        return "I couldn't find relevant information in the uploaded document."

    print(f"Retrieved {len(retrieved_chunks)} chunks.")

    # Step 2: Build prompt
    prompt = build_prompt(question, retrieved_chunks)

    print("\nGenerating answer using Qwen...")

    # Step 3: Generate answer
    answer = generate_answer(prompt)

    return answer


# Main program
if __name__ == "__main__":

    question = input("\nAsk a question about your PDF: ")

    answer = rag_pipeline(question)

    print("\n========== RAG ANSWER ==========\n")
    print(answer)
    print("\n================================")
