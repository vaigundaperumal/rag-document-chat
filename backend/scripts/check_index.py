import os
from dotenv import load_dotenv
from pinecone import Pinecone

load_dotenv()

pc = Pinecone(api_key=os.getenv("PINECONE_API_KEY"))

index_info = pc.indexes.describe("rag-document-chat")

print("Index name:", index_info.name)
print("Index schema:")
print(index_info.schema)