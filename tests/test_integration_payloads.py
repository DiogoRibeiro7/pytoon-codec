"""
Integration tests with realistic mixed payloads combining scalars, arrays, and tables.

These tests simulate real-world LLM prompt payloads with time-series data,
nested events, and complex structured data.
"""

import pytest

from pytoon_codec import ToonCodec


@pytest.mark.integration
def test_integration_analytics_dashboard_payload() -> None:
    """Test encoding/decoding a realistic analytics dashboard payload."""
    codec = ToonCodec()

    data = {
        "dashboard_id": "dash-001",
        "title": "Website Analytics",
        "date_range": "2025-01-01 to 2025-01-07",
        "total_users": 1520,
        "active": True,
        "tags": ["analytics", "web", "production"],
        "metrics": [
            {"date": "2025-01-01", "views": 1250, "clicks": 89, "conversions": 12},
            {"date": "2025-01-02", "views": 1340, "clicks": 102, "conversions": 15},
            {"date": "2025-01-03", "views": 1180, "clicks": 76, "conversions": 8},
        ],
        "top_pages": [
            {"url": "/home", "visits": 450},
            {"url": "/products", "visits": 320},
            {"url": "/about", "visits": 180},
        ],
    }

    toon = codec.encode(data)
    decoded = codec.decode(toon)

    assert decoded == data


@pytest.mark.integration
def test_integration_iot_sensor_events_payload() -> None:
    """Test encoding/decoding IoT sensor events with nested payloads."""
    codec = ToonCodec()

    data = {
        "device_id": "sensor-bathroom-01",
        "location": "bathroom",
        "firmware_version": "1.2.3",
        "battery_level": 87.5,
        "online": True,
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
            {
                "timestamp": "2025-01-15T08:40:00Z",
                "type": "light",
                "payload": {
                    "sensor": "ceiling_light",
                    "room": "bathroom",
                    "zone": "main",
                },
                "user": {"id": 123, "name": "Alice"},
            },
        ],
    }

    toon = codec.encode(data)
    decoded = codec.decode(toon)

    assert decoded == data


@pytest.mark.integration
def test_integration_mixed_scalars_arrays_tables() -> None:
    """Test realistic payload with scalars, primitive arrays, and object arrays."""
    codec = ToonCodec()

    data = {
        "experiment_id": "exp-001",
        "version": 2,
        "active": True,
        "notes": None,
        "tags": ["ml", "production", "batch-processing"],
        "metadata": {
            "environment": "prod",
            "region": "us-east-1",
            "owner": {"id": "u-456", "email": "researcher@example.com"},
        },
        "metrics": [
            {"timestamp": "2025-01-01T00:00:00Z", "accuracy": 0.95, "loss": 0.12},
            {"timestamp": "2025-01-01T01:00:00Z", "accuracy": 0.96, "loss": 0.10},
            {"timestamp": "2025-01-01T02:00:00Z", "accuracy": 0.97, "loss": 0.08},
        ],
        "checkpoints": [
            {"epoch": 1, "path": "/models/ckpt-1.pt", "size_mb": 450},
            {"epoch": 5, "path": "/models/ckpt-5.pt", "size_mb": 452},
        ],
    }

    toon = codec.encode(data)
    decoded = codec.decode(toon)

    assert decoded == data


@pytest.mark.integration
def test_integration_timeseries_and_nested_events() -> None:
    """Test time-series metrics combined with nested event logs."""
    codec = ToonCodec()

    payload = {
        "report_id": "daily-report-2025-01-01",
        "generated_at": "2025-01-02T00:00:00Z",
        "metrics": [
            {"date": "2025-01-01", "views": 1500, "clicks": 120, "revenue": 450.50},
            {"date": "2025-01-02", "views": 1620, "clicks": 135, "revenue": 523.75},
        ],
        "events": [
            {
                "timestamp": "2025-01-01T08:00:00Z",
                "event_type": "user_login",
                "payload": {"device": "mobile", "os": "iOS"},
                "user": {"id": "u-123", "tier": "premium"},
            },
            {
                "timestamp": "2025-01-01T08:05:00Z",
                "event_type": "purchase",
                "payload": {"device": "mobile", "os": "iOS"},
                "user": {"id": "u-123", "tier": "premium"},
            },
            {
                "timestamp": "2025-01-01T10:30:00Z",
                "event_type": "user_logout",
                "payload": {"device": "mobile", "os": "iOS"},
                "user": {"id": "u-123", "tier": "premium"},
            },
        ],
    }

    toon = codec.encode(payload)
    decoded = codec.decode(toon)

    assert decoded == payload


@pytest.mark.integration
def test_integration_monitoring_alerts_payload() -> None:
    """Test monitoring system alerts with nested context."""
    codec = ToonCodec()

    data = {
        "system": "monitoring-prod",
        "alert_count": 3,
        "severity_threshold": "warning",
        "enabled": True,
        "notification_channels": ["email", "slack", "pagerduty"],
        "alerts": [
            {
                "timestamp": "2025-01-15T10:00:00Z",
                "severity": "critical",
                "message": "High CPU usage detected",
                "context": {
                    "host": "server-01",
                    "metric": "cpu_percent",
                    "value": 95.5,
                },
            },
            {
                "timestamp": "2025-01-15T10:05:00Z",
                "severity": "warning",
                "message": "Memory usage above threshold",
                "context": {
                    "host": "server-02",
                    "metric": "memory_percent",
                    "value": 82.3,
                },
            },
            {
                "timestamp": "2025-01-15T10:10:00Z",
                "severity": "info",
                "message": "Deployment completed successfully",
                "context": {
                    "host": "server-03",
                    "metric": "deployment_status",
                    "value": 1.0,
                },
            },
        ],
    }

    toon = codec.encode(data)
    decoded = codec.decode(toon)

    assert decoded == data


@pytest.mark.integration
def test_integration_llm_prompt_context_payload() -> None:
    """Test a realistic LLM prompt context with conversation history."""
    codec = ToonCodec()

    data = {
        "session_id": "chat-session-789",
        "user_id": "u-999",
        "model": "gpt-4",
        "temperature": 0.7,
        "max_tokens": 2000,
        "conversation_history": [
            {
                "timestamp": "2025-01-15T14:00:00Z",
                "role": "user",
                "content": "What is TOON encoding?",
                "metadata": {"length": 24, "language": "en"},
            },
            {
                "timestamp": "2025-01-15T14:00:05Z",
                "role": "assistant",
                "content": "TOON is a token-efficient serialization format...",
                "metadata": {"length": 150, "language": "en"},
            },
            {
                "timestamp": "2025-01-15T14:01:00Z",
                "role": "user",
                "content": "Can you show an example?",
                "metadata": {"length": 28, "language": "en"},
            },
        ],
    }

    toon = codec.encode(data)
    decoded = codec.decode(toon)

    assert decoded == data


@pytest.mark.integration
def test_integration_large_timeseries_payload() -> None:
    """Test encoding/decoding a larger time-series dataset."""
    codec = ToonCodec()

    # Generate 24 hours of hourly data
    hours = []
    for hour in range(24):
        hours.append(
            {
                "hour": f"{hour:02d}:00",
                "temperature": 20.0 + (hour % 12) * 0.5,
                "humidity": 60 + (hour % 10),
                "active": hour >= 6 and hour <= 22,  # Active during day
            }
        )

    data = {
        "station_id": "weather-station-01",
        "date": "2025-01-15",
        "location": "San Francisco",
        "readings": hours,
    }

    toon = codec.encode(data)
    decoded = codec.decode(toon)

    assert decoded == data
    assert len(decoded["readings"]) == 24


@pytest.mark.integration
def test_integration_empty_collections_in_payload() -> None:
    """Test payload with some empty arrays and tables."""
    codec = ToonCodec()

    data = {
        "report_id": "report-empty-001",
        "status": "pending",
        "tags": [],  # empty primitive array
        "errors": [],  # empty object array
        "metrics": [{"date": "2025-01-01", "value": 100}],
        "warnings": [],  # another empty array
    }

    toon = codec.encode(data)
    decoded = codec.decode(toon)

    assert decoded == data


@pytest.mark.integration
def test_integration_special_characters_throughout_payload() -> None:
    """Test payload with special characters in various fields."""
    codec = ToonCodec()

    data = {
        "title": "Report: Q1, 2025",
        "description": 'Multi-line\ndescription with special chars: comma, quote"',
        "tags": ["tag-1", "tag, with comma", "tag with spaces  "],
        "events": [
            {
                "name": "Event A",
                "description": 'Contains: commas, newlines\nand quotes"',
                "metadata": {"key": "value, with comma", "note": "Trailing spaces  "},
            }
        ],
    }

    toon = codec.encode(data)
    decoded = codec.decode(toon)

    assert decoded == data
