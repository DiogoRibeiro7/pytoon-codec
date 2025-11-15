"""Basic time-series encoding/decoding example for pytoon-codec.

Run with:
    poetry run python examples/time_series_basic.py
"""

from __future__ import annotations

from datetime import date

from pytoon_codec import ToonCodec


def build_metrics_payload() -> dict:
    """Return a small metrics payload keyed by ISO dates."""
    base = date(2025, 1, 1)
    metrics = []
    for offset, views, clicks in [
        (0, 1250, 89),
        (1, 1340, 102),
        (2, 1180, 76),
    ]:
        metrics.append(
            {
                "date": (base.fromordinal(base.toordinal() + offset)).isoformat(),
                "views": views,
                "clicks": clicks,
            }
        )

    return {
        "project": "analytics-dashboard",
        "metrics": metrics,
    }


def main() -> None:
    codec = ToonCodec()
    payload = build_metrics_payload()

    toon = codec.encode(payload)
    print("Encoded TOON:\n")
    print(toon)
    print("\nDecoded payload:")
    decoded = codec.decode(toon)
    print(decoded)

    assert decoded == payload, "Round-trip mismatch!"


if __name__ == "__main__":
    main()
