"""
Unit tests for tabular array encoding/decoding.
"""

import pytest

from pytoon_codec import ToonCodec, ToonDecodingError, ToonEncodingError


@pytest.mark.unit
def test_encode_decode_simple_table() -> None:
    """Test basic tabular encoding with two rows."""
    codec = ToonCodec()

    data = {
        "metrics": [
            {"date": "2025-01-01", "value": 100},
            {"date": "2025-01-02", "value": 120},
        ]
    }

    toon = codec.encode(data)
    assert "metrics[2]{date,value}:" in toon

    decoded = codec.decode(toon)
    assert decoded == data


@pytest.mark.unit
def test_encode_decode_table_single_row() -> None:
    """Test table with a single row."""
    codec = ToonCodec()

    data = {"users": [{"id": 1, "name": "Alice"}]}

    toon = codec.encode(data)
    assert "users[1]{id,name}:" in toon

    decoded = codec.decode(toon)
    assert decoded == data


@pytest.mark.unit
def test_encode_decode_table_multiple_columns() -> None:
    """Test table with many columns."""
    codec = ToonCodec()

    data = {
        "readings": [
            {
                "ts": "2025-01-01T00:00:00Z",
                "temp": 20.5,
                "humidity": 65,
                "active": True,
            },
            {
                "ts": "2025-01-01T01:00:00Z",
                "temp": 21.0,
                "humidity": 63,
                "active": True,
            },
        ]
    }

    toon = codec.encode(data)

    decoded = codec.decode(toon)
    assert decoded == data


@pytest.mark.unit
def test_encode_decode_table_with_null_values() -> None:
    """Test table containing null values."""
    codec = ToonCodec()

    data = {
        "events": [
            {"ts": "2025-01-01", "error": None},
            {"ts": "2025-01-02", "error": "timeout"},
        ]
    }

    toon = codec.encode(data)
    assert "null" in toon

    decoded = codec.decode(toon)
    assert decoded == data


@pytest.mark.unit
def test_encode_decode_table_with_bool_values() -> None:
    """Test table with boolean columns."""
    codec = ToonCodec()

    data = {
        "flags": [
            {"name": "feature_a", "enabled": True},
            {"name": "feature_b", "enabled": False},
        ]
    }

    toon = codec.encode(data)

    decoded = codec.decode(toon)
    assert decoded == data


@pytest.mark.unit
def test_encode_decode_empty_table() -> None:
    """Test that empty array of objects is encoded as [0]{}: with no columns."""
    codec = ToonCodec()
    data = {"items": []}

    toon = codec.encode(data)
    assert "items[0]:" in toon

    decoded = codec.decode(toon)
    assert decoded == data


@pytest.mark.unit
def test_encode_table_inconsistent_row_fields_raises() -> None:
    """Test that rows with different field sets raise ToonEncodingError."""
    codec = ToonCodec()

    data = {
        "metrics": [
            {"date": "2025-01-01", "value": 1},
            {"date": "2025-01-02"},  # missing 'value' field
        ]
    }

    with pytest.raises(ToonEncodingError, match="homogeneous"):
        codec.encode(data)


@pytest.mark.unit
def test_encode_table_extra_field_in_second_row_raises() -> None:
    """Test that extra fields in later rows raise ToonEncodingError."""
    codec = ToonCodec()

    data = {
        "metrics": [
            {"date": "2025-01-01", "value": 1},
            {"date": "2025-01-02", "value": 2, "extra": "field"},  # extra field
        ]
    }

    with pytest.raises(ToonEncodingError, match="homogeneous"):
        codec.encode(data)


@pytest.mark.unit
def test_decode_table_row_column_count_mismatch_raises() -> None:
    """Test that row with wrong number of cells raises ToonDecodingError."""
    codec = ToonCodec()

    toon = """metrics[2]{date,value}:
  2025-01-01,100
  2025-01-02"""  # missing value cell

    with pytest.raises(ToonDecodingError, match="has 1 cells"):
        codec.decode(toon)


@pytest.mark.unit
def test_decode_table_row_count_mismatch_too_few_raises() -> None:
    """Test that fewer rows than declared raises ToonDecodingError."""
    codec = ToonCodec()

    toon = """metrics[3]{date,value}:
  2025-01-01,100
  2025-01-02,120"""  # declares 3 rows, only 2 provided

    with pytest.raises(ToonDecodingError, match="declares 3 rows"):
        codec.decode(toon)


@pytest.mark.unit
def test_decode_table_row_count_mismatch_too_many_raises() -> None:
    """Test that more rows than declared raises ToonDecodingError."""
    codec = ToonCodec()

    toon = """metrics[1]{date,value}:
  2025-01-01,100
  2025-01-02,120"""  # declares 1 row, but 2 provided

    with pytest.raises(ToonDecodingError, match="declares 1 rows"):
        codec.decode(toon)


@pytest.mark.unit
def test_decode_table_with_no_fields_raises() -> None:
    """Test that table header with no fields raises ToonDecodingError."""
    codec = ToonCodec()

    toon = """metrics[2]{}:
  2025-01-01,100
  2025-01-02,120"""

    with pytest.raises(ToonDecodingError, match="at least one field"):
        codec.decode(toon)


@pytest.mark.unit
def test_decode_table_invalid_header_syntax_raises() -> None:
    """Test that malformed table header raises ToonDecodingError."""
    codec = ToonCodec()

    # Missing closing brace
    toon = """metrics[2]{date,value:
  2025-01-01,100"""

    with pytest.raises(ToonDecodingError):
        codec.decode(toon)


@pytest.mark.unit
def test_decode_table_preserves_column_order() -> None:
    """Test that column order is preserved during round-trip."""
    codec = ToonCodec()

    toon = """items[2]{id,name,active}:
  1,Alice,true
  2,Bob,false"""

    decoded = codec.decode(toon)

    # Check that the first dict has keys in the same order
    first_item = decoded["items"][0]
    keys = list(first_item.keys())
    assert keys == ["id", "name", "active"]


@pytest.mark.unit
def test_encode_table_with_special_characters_in_cells() -> None:
    """Test that cells with commas or quotes are properly escaped."""
    codec = ToonCodec()

    data = {
        "events": [
            {"id": 1, "msg": "hello, world"},
            {"id": 2, "msg": 'say "hi"'},
        ]
    }

    toon = codec.encode(data)
    decoded = codec.decode(toon)

    assert decoded == data


@pytest.mark.unit
def test_decode_table_type_inference_in_cells() -> None:
    """Test that cell values are correctly typed (int, float, bool, null, str)."""
    codec = ToonCodec()

    toon = """data[2]{id,ratio,active,error,name}:
  1,3.14,true,null,Alice
  2,2.71,false,null,Bob"""

    decoded = codec.decode(toon)

    assert decoded == {
        "data": [
            {"id": 1, "ratio": 3.14, "active": True, "error": None, "name": "Alice"},
            {"id": 2, "ratio": 2.71, "active": False, "error": None, "name": "Bob"},
        ]
    }
