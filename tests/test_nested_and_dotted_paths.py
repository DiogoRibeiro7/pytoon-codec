"""
Unit tests for nested object flattening, dotted path expansion, and related edge cases.
"""

import pytest

from pytoon_codec import ToonCodec, ToonDecodingError, ToonEncodingError


@pytest.mark.unit
def test_encode_decode_nested_object_single_level() -> None:
    """Test flattening and expanding single-level nested object."""
    codec = ToonCodec(expand_paths=True)

    data = {"user": {"id": 123, "name": "Alice"}}

    toon = codec.encode(data)
    assert "user.id:" in toon or "user.id" in toon
    assert "user.name:" in toon or "user.name" in toon

    decoded = codec.decode(toon)
    assert decoded == data


@pytest.mark.unit
def test_encode_decode_nested_object_multi_level() -> None:
    """Test flattening and expanding multi-level nested objects."""
    codec = ToonCodec(expand_paths=True)

    data = {
        "metadata": {
            "user": {"profile": {"id": "u-1", "role": "admin"}},
            "source": "test",
        }
    }

    toon = codec.encode(data)
    assert "metadata.user.profile.id:" in toon
    assert "metadata.user.profile.role:" in toon
    assert "metadata.source:" in toon

    decoded = codec.decode(toon)
    assert decoded == data


@pytest.mark.unit
def test_encode_nested_object_with_various_types() -> None:
    """Test nested object with different primitive types."""
    codec = ToonCodec(expand_paths=True)

    data = {
        "config": {"enabled": True, "port": 8080, "timeout": 30.5, "description": None}
    }

    toon = codec.encode(data)
    decoded = codec.decode(toon)

    assert decoded == data


@pytest.mark.unit
def test_decode_with_expand_paths_true() -> None:
    """Test that expand_paths=True reconstructs nested dicts."""
    codec = ToonCodec(expand_paths=True)

    toon = """metadata.user.id: u-1
metadata.user.role: admin
metadata.source: test
"""

    decoded = codec.decode(toon)

    assert decoded == {
        "metadata": {"user": {"id": "u-1", "role": "admin"}, "source": "test"}
    }


@pytest.mark.unit
def test_decode_with_expand_paths_false() -> None:
    """Test that expand_paths=False keeps dotted keys flat."""
    codec = ToonCodec(expand_paths=False)

    toon = """metadata.user.id: u-1
metadata.user.role: admin
"""

    decoded = codec.decode(toon)

    assert decoded == {
        "metadata.user.id": "u-1",
        "metadata.user.role": "admin",
    }


@pytest.mark.unit
def test_encode_nested_arrays_in_object_raises() -> None:
    """Test that arrays nested inside objects raise ToonEncodingError."""
    codec = ToonCodec()

    data = {
        "metadata": {
            "tags": ["a", "b", "c"],  # array inside nested object: unsupported
        }
    }

    with pytest.raises(ToonEncodingError, match="Arrays nested inside objects"):
        codec.encode(data)


@pytest.mark.unit
def test_encode_nested_arrays_in_deep_object_raises() -> None:
    """Test that arrays deeply nested inside objects raise ToonEncodingError."""
    codec = ToonCodec()

    data = {
        "level1": {
            "level2": {
                "tags": ["x", "y"]  # deeply nested array
            }
        }
    }

    with pytest.raises(ToonEncodingError, match="Arrays nested inside objects"):
        codec.encode(data)


@pytest.mark.unit
def test_encode_table_with_nested_objects_in_rows() -> None:
    """Test that nested objects in table rows are flattened into dotted columns."""
    codec = ToonCodec(expand_paths=True)

    data = {
        "events": [
            {"ts": "2025-01-01", "user": {"id": 1, "name": "Alice"}},
            {"ts": "2025-01-02", "user": {"id": 2, "name": "Bob"}},
        ]
    }

    toon = codec.encode(data)
    assert "events[2]{ts,user.id,user.name}:" in toon

    decoded = codec.decode(toon)
    assert decoded == data


@pytest.mark.unit
def test_encode_table_with_deep_nested_objects_in_rows() -> None:
    """Test that deeply nested objects in rows are flattened correctly."""
    codec = ToonCodec(expand_paths=True)

    data = {
        "events": [
            {
                "ts": "2025-01-01",
                "payload": {"sensor": {"type": "motion", "location": "bedroom"}},
            }
        ]
    }

    toon = codec.encode(data)
    assert "payload.sensor.type" in toon
    assert "payload.sensor.location" in toon

    decoded = codec.decode(toon)
    assert decoded == data


@pytest.mark.unit
def test_encode_table_with_arrays_in_rows_raises() -> None:
    """Test that arrays inside table rows raise ToonEncodingError."""
    codec = ToonCodec()

    data = {
        "events": [
            {
                "ts": "2025-01-01",
                "tags": ["a", "b"],  # array inside row: unsupported
            }
        ]
    }

    with pytest.raises(ToonEncodingError, match="Arrays nested inside tabular rows"):
        codec.encode(data)


@pytest.mark.unit
def test_decode_path_conflict_scalar_vs_object_raises() -> None:
    """Test that path conflict (scalar vs nested object) raises ToonDecodingError."""
    codec = ToonCodec(expand_paths=True)

    # 'metadata' is set to a scalar, but we also need 'metadata.user'
    toon = """metadata: some_value
metadata.user: another_value
"""

    with pytest.raises(ToonDecodingError, match="conflict"):
        codec.decode(toon)


@pytest.mark.unit
def test_decode_path_conflict_duplicate_key_raises() -> None:
    """Test that duplicate keys raise ToonDecodingError."""
    codec = ToonCodec(expand_paths=True)

    toon = """user.id: 1
user.id: 2
"""

    with pytest.raises(ToonDecodingError, match="already exists"):
        codec.decode(toon)


@pytest.mark.unit
def test_encode_mixed_nested_and_flat_keys() -> None:
    """Test encoding data with both nested objects and top-level scalars."""
    codec = ToonCodec(expand_paths=True)

    data = {
        "version": 1,
        "config": {"host": "localhost", "port": 5432},
        "enabled": True,
    }

    toon = codec.encode(data)
    decoded = codec.decode(toon)

    assert decoded == data


@pytest.mark.unit
def test_roundtrip_preserves_structure_with_expand_paths() -> None:
    """Test complete round-trip with expand_paths=True preserves structure."""
    codec = ToonCodec(expand_paths=True)

    data = {
        "app": {
            "name": "test-app",
            "version": "1.0.0",
            "config": {"db": {"host": "localhost", "port": 5432}},
        }
    }

    toon = codec.encode(data)
    decoded = codec.decode(toon)

    assert decoded == data


@pytest.mark.unit
def test_roundtrip_flat_keys_with_expand_paths_false() -> None:
    """Test round-trip with expand_paths=False keeps keys flat."""
    codec_encode = ToonCodec(expand_paths=True)
    codec_decode = ToonCodec(expand_paths=False)

    data = {"user": {"id": 123, "name": "Alice"}}

    toon = codec_encode.encode(data)
    decoded = codec_decode.decode(toon)

    # Should be flat
    assert decoded == {"user.id": 123, "user.name": "Alice"}
