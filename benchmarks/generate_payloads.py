"""Utility builders for synthetic benchmark payloads."""

from __future__ import annotations

from datetime import datetime, timedelta
from typing import Any

from pytoon_codec import ToonCodec

__all__ = ["generate_events", "generate_metrics", "roundtrip"]


def generate_metrics(n_rows: int, *, start: datetime | None = None) -> dict[str, Any]:
    """
    Create a metrics payload with monotonically increasing timestamp rows.
    """
    if n_rows <= 0:
        raise ValueError("n_rows must be positive")

    base = start or datetime(2025, 1, 1)
    rows: list[dict[str, Any]] = []
    for idx in range(n_rows):
        current = base + timedelta(minutes=idx * 10)
        rows.append(
            {
                "timestamp": current.isoformat(),
                "views": 1000 + idx * 3,
                "clicks": 50 + (idx % 20),
                "conversion_rate": round(0.05 + (idx % 10) * 0.001, 4),
            }
        )

    return {
        "dashboard": "benchmarks-demo",
        "window": {
            "start": base.isoformat(),
            "end": (base + timedelta(minutes=(n_rows - 1) * 10)).isoformat(),
        },
        "metrics": rows,
    }


def generate_events(n_rows: int, *, start: datetime | None = None) -> dict[str, Any]:
    """
    Create a nested event log payload with repeated users/payloads.
    """
    if n_rows <= 0:
        raise ValueError("n_rows must be positive")

    base = start or datetime(2025, 2, 1, 8, 0, 0)
    users = [
        {"id": 101, "name": "Alice"},
        {"id": 202, "name": "Bob"},
        {"id": 303, "name": "Charlie"},
    ]
    sensors = [
        ("motion", "sensor_motion"),
        ("door", "sensor_door"),
        ("light", "sensor_light"),
    ]

    rows: list[dict[str, Any]] = []
    for idx in range(n_rows):
        ts = base + timedelta(seconds=idx * 45)
        event_type, sensor_name = sensors[idx % len(sensors)]
        user = users[idx % len(users)]
        rows.append(
            {
                "timestamp": ts.isoformat() + "Z",
                "type": event_type,
                "payload": {
                    "sensor": sensor_name,
                    "room": "bathroom" if idx % 2 == 0 else "kitchen",
                    "zone": "main" if idx % 3 == 0 else "entry",
                },
                "user": user,
            }
        )

    return {
        "device_id": "iot-benchmark-unit",
        "firmware_version": "1.2.3",
        "events": rows,
    }


def roundtrip(codec: ToonCodec, payload: dict[str, Any]) -> None:
    toon = codec.encode(payload)
    codec.decode(toon)
