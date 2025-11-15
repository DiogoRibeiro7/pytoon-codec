from pytoon_codec import ToonCodec


def test_integration_timeseries_and_nested_events() -> None:
    codec = ToonCodec()

    payload = {
        "metrics": [
            {"date": "2025-01-01", "views": 100, "clicks": 10},
            {"date": "2025-01-02", "views": 120, "clicks": 15},
        ],
        "events": [
            {
                "ts": "2025-01-01T08:00:00Z",
                "type": "bed_exit",
                "payload": {"sensor": "bed-1", "room": "bedroom"},
                "user": {"id": "u-123"},
            },
            {
                "ts": "2025-01-01T08:05:00Z",
                "type": "kettle_on",
                "payload": {"sensor": "kettle-1", "room": "kitchen"},
                "user": {"id": "u-123"},
            },
        ],
    }

    toon = codec.encode(payload)
    decoded = codec.decode(toon)

    assert decoded == payload
