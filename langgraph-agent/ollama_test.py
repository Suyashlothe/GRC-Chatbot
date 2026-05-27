import httpx

BASE_URL = "http://157.20.214.158:11434"
MODEL    = "minimax-m2.1:cloud"


def chat(prompt: str) -> str:
    payload = {
        "model": MODEL,
        "messages": [
            {
                "role":    "system",
                "content": "You are a GRC assistant."
            },
            {
                "role":    "user",
                "content": prompt
            }
        ],
        "stream": False
    }

    response = httpx.post(
        f"{BASE_URL}/api/chat",
        json=payload,
        timeout=120,
    )

    response.raise_for_status()
    return response.json()["message"]["content"]


if __name__ == "__main__":
    prompt = "What is ISO 27001?"
    print(f"Prompt: {prompt}\n")

    answer = chat(prompt)
    print(f"Response: {answer}")