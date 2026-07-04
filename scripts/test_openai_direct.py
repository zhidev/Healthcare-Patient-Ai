"""Direct OpenAI API smoke test without fallback."""

import os

from dotenv import load_dotenv
from openai import OpenAI


def mask_key(key: str | None) -> str:
    if not key:
        return "NOT LOADED"

    return f"{key[:7]}...{key[-4:]}"


def main():
    load_dotenv(override=True)

    api_key = os.getenv("OPENAI_API_KEY")
    model = os.getenv("OPENAI_MODEL", "gpt-5.4-mini")

    print("API key:", mask_key(api_key))
    print("Model:", model)

    client = OpenAI(api_key=api_key)

    response = client.responses.create(
        model=model,
        input="Reply with exactly: API test worked",
        max_output_tokens=80,
    )

    print("Response:", response.output_text)
    print("Usage:", response.usage)


if __name__ == "__main__":
    main()