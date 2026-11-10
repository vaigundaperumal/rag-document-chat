import os
from dotenv import load_dotenv

load_dotenv()

api_key = os.getenv("PINECONE_API_KEY")

if api_key:
    print("Pinecone API key loaded successfully!")
else:
    print("Pinecone API key not found!")