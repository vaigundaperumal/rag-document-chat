
import requests


def generate_answer(prompt):

    url = "http://localhost:11434/api/generate"

    payload = {
        "model": "qwen2.5:1.5b",
        "prompt": prompt,
        "stream": False
    }

    response = requests.post(
        url,
        json=payload,
        timeout=180
    )

    response.raise_for_status()

    result = response.json()

    return result["response"]
