"""Nested events encoding/decoding example for pytoon-codec.

Run with:
    poetry run python examples/nested_events_basic.py
"""

from __future__ import annotations

from pytoon_codec import ToonCodec


def build_events_payload() -> dict:
    """Return a small payload representing nested bathroom sensor events."""
    return {
        "log_title": "Bathroom Sensor Events",
        "events": [
            {
                "timestamp": "2025-01-15T08:30:00Z",
                "type": "motion",
                "payload": {"sensor": "toilet", "room": "bathroom", "zone": "main"},
                "user": {"id": 123, "name": "Alice"},
            },
            {
                "timestamp": "2025-01-15T08:35:00Z",
                "type": "door",
                "payload": {"sensor": "main_door", "room": "bathroom", "zone": "entry"},
                "user": {"id": 123, "name": "Alice"},
            },
        ],
    }


def main() -> None:
    codec = ToonCodec()
    payload = build_events_payload()

    toon = codec.encode(payload)
    print("Encoded TOON:\n")
    print(toon)
    print("\nDecoded payload:")
    decoded = codec.decode(toon)
    print(decoded)

    assert decoded == payload, "Round-trip mismatch!"


if __name__ == "__main__":
    main()
