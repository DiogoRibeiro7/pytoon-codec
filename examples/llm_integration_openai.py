"""Example of embedding TOON data in an OpenAI prompt."""

from __future__ import annotations

from pytoon_codec import ToonCodec


def build_example_payload() -> dict:
    return {
        "metrics": [
            {"date": "2025-01-01", "views": 1250, "clicks": 89},
            {"date": "2025-01-02", "views": 1340, "clicks": 102},
            {"date": "2025-01-03", "views": 1180, "clicks": 76},
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

    prompt = f"""You are a data assistant.

Here is structured data in TOON format:

{toon}

Summarise the main trends in 3 bullet points."""

    print("Prompt preview:\n")
    print(prompt)

    # Example (commented) OpenAI call:
    # Requires: `pip install openai` and `OPENAI_API_KEY` in env.
    #
    # from openai import OpenAI
    # client = OpenAI()
    # response = client.chat.completions.create(
    #     model="gpt-4o-mini",
    #     messages=[
    #         {"role": "system", "content": "You are a helpful data assistant."},
    #         {"role": "user", "content": prompt},
    #     ],
    # )
    # print(response.choices[0].message.content)


if __name__ == "__main__":
    main()
