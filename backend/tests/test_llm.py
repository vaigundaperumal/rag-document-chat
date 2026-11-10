
from services.llm import generate_answer

prompt = """
Explain machine learning in three simple sentences.
"""

answer = generate_answer(prompt)

print("AI Response:")
print(answer)
