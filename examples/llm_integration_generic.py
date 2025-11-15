"""Generic LLM integration example using a placeholder client."""

from __future__ import annotations

from typing import Protocol

from pytoon_codec import ToonCodec


class LLMClient(Protocol):
    def call(self, model_name: str, prompt: str) -> str: ...


def call_llm(model_name: str, prompt: str) -> str:
    # Placeholder for your actual LLM call (e.g., Bedrock, Azure, local model)
    # return some_sdk.generate(model=model_name, prompt=prompt)
    return f"[example response from {model_name}]"


def build_example_payload() -> dict:
    return {
        "metrics": [
            {"date": "2025-01-01", "views": 1250, "clicks": 89},
            {"date": "2025-01-02", "views": 1340, "clicks": 102},
        ],
        "events": [
            {
                "timestamp": "2025-01-15T08:30:00Z",
                "type": "motion",
                "payload": {"sensor": "toilet", "room": "bathroom"},
                "user": {"id": 123, "name": "Alice"},
            }
        ],
    }


def main() -> None:
    codec = ToonCodec()
    payload = build_example_payload()
    toon = codec.encode(payload)

    prompt = f"""Summarise the following structured telemetry (TOON format).

{toon}

Return insights in plain English."""

    result = call_llm("my-llm", prompt)
    print(result)

    # If the LLM responds with TOON, decode back:
    # decoded = codec.decode(result_from_llm)


if __name__ == "__main__":
    main()
