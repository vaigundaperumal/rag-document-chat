from sentence_transformers import SentenceTransformer

# Load the model
model = SentenceTransformer("sentence-transformers/all-MiniLM-L6-v2")


def generate_embeddings(chunks):

    texts = [
        chunk["content"]
        for chunk in chunks
    ]

    embeddings = model.encode(texts)

    return embeddings.tolist()