from pytoon_codec import ToonCodec


def test_integration_mixed_scalars_arrays_tables() -> None:
    codec = ToonCodec()

    data = {
        "version": 1,
        "tags": ["a", "b"],
        "metadata": {
            "experiment": "exp-001",
            "env": "prod",
        },
        "metrics": [
            {"ts": "2025-01-01T00:00:00Z", "value": 1.0},
            {"ts": "2025-01-01T01:00:00Z", "value": 1.5},
        ],
        "events": [
            {
                "ts": "2025-01-01T10:00:00Z",
                "type": "toilet",
                "payload": {"sensor": "toilet-1", "room": "bathroom"},
            },
            {
                "ts": "2025-01-01T11:00:00Z",
                "type": "kettle",
                "payload": {"sensor": "kettle-1", "room": "kitchen"},
            },
        ],
    }

    toon = codec.encode(data)
    decoded = codec.decode(toon)

    assert decoded == data
