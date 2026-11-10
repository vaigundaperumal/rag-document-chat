
import os
import time

from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index = pc.index("rag-document-chat")


def store_chunks(chunks, embeddings, filename, namespace):

    documents = []

    for i, chunk in enumerate(chunks):

        documents.append({
            "_id": f"pdf-chunk-{i+1}",
            "embedding": embeddings[i],
            "content": chunk["content"],
            "page_number": chunk["page_number"],
            "filename": filename
        })

    response = index.documents.upsert(
        namespace=namespace,
        documents=documents
    )

    return response


def wait_until_stored(namespace, chunks):

    ids = [
        f"pdf-chunk-{i+1}"
        for i in range(len(chunks))
    ]

    for attempt in range(15):

        response = index.documents.fetch(
            namespace=namespace,
            ids=ids
        )

        if len(response.documents) == len(ids):
            return True

        time.sleep(1)

    return False


def delete_namespace_documents(namespace):

    index.documents.delete(
        namespace=namespace,
        delete_all=True
    )
