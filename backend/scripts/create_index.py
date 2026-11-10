import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

INDEX_NAME = "rag-document-chat"

# Delete the old index if it exists
if pc.indexes.exists(INDEX_NAME):
    pc.indexes.delete(INDEX_NAME)
    print("Old index deleted!")

# Create a new index with our local embedding model
pc.indexes.create(
    name=INDEX_NAME,
    schema={
        "fields": {
            "embedding": {
                "type": "dense_vector",
                "dimension": 384,
                "metric": "cosine"
            }
        }
    },
    deployment={
        "deployment_type": "managed",
        "cloud": "aws",
        "region": "us-east-1"
    }
)

print("New index created successfully!")

index_info = pc.indexes.describe(INDEX_NAME)
print("Index ready:", index_info.status.ready)
print("Schema:", index_info.schema)