
from services.prompt_builder import build_prompt

question = "What are the types of machine learning?"

retrieved_chunks = [
    {
        "page_number": 2,
        "content": "Machine learning includes supervised, unsupervised and reinforcement learning."
    },
    {
        "page_number": 3,
        "content": "Supervised learning uses labelled training data."
    }
]

prompt = build_prompt(question, retrieved_chunks)

print(prompt)
