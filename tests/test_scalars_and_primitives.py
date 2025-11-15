"""
Unit tests for scalar encoding/decoding and primitive values.
"""

import pytest

from pytoon_codec import ToonCodec, ToonDecodingError


@pytest.mark.unit
def test_encode_decode_simple_scalars() -> None:
    """Test basic scalar types round-trip correctly."""
    codec = ToonCodec()

    data = {
        "flag": True,
        "count": 42,
        "ratio": 0.5,
        "msg": "hello",
        "empty": None,
    }

    toon = codec.encode(data)
    decoded = codec.decode(toon)

    assert decoded == data


@pytest.mark.unit
def test_encode_scalar_bool_true() -> None:
    """Test boolean true is encoded as 'true'."""
    codec = ToonCodec()
    data = {"active": True}
    toon = codec.encode(data)
    assert "active: true" in toon


@pytest.mark.unit
def test_encode_scalar_bool_false() -> None:
    """Test boolean false is encoded as 'false'."""
    codec = ToonCodec()
    data = {"active": False}
    toon = codec.encode(data)
    assert "active: false" in toon


@pytest.mark.unit
def test_encode_scalar_null() -> None:
    """Test None is encoded as 'null'."""
    codec = ToonCodec()
    data = {"value": None}
    toon = codec.encode(data)
    assert "value: null" in toon


@pytest.mark.unit
def test_encode_scalar_integer() -> None:
    """Test integers are encoded as plain numbers."""
    codec = ToonCodec()
    data = {"count": 42}
    toon = codec.encode(data)
    assert "count: 42" in toon


@pytest.mark.unit
def test_encode_scalar_float() -> None:
    """Test floats are encoded as plain numbers."""
    codec = ToonCodec()
    data = {"ratio": 3.14}
    toon = codec.encode(data)
    assert "ratio: 3.14" in toon


@pytest.mark.unit
def test_encode_scalar_negative_number() -> None:
    """Test negative numbers are encoded correctly."""
    codec = ToonCodec()
    data = {"temp": -10}
    toon = codec.encode(data)
    assert "temp: -10" in toon


@pytest.mark.unit
def test_encode_scalar_simple_string() -> None:
    """Test simple strings without special chars are unquoted."""
    codec = ToonCodec()
    data = {"name": "Alice"}
    toon = codec.encode(data)
    assert "name: Alice" in toon


@pytest.mark.unit
def test_encode_scalar_with_comma_uses_quotes() -> None:
    """Test strings containing commas are JSON-quoted."""
    codec = ToonCodec()
    data = {"text": "hello, world"}
    toon = codec.encode(data)
    assert 'text: "hello, world"' in toon

    decoded = codec.decode(toon)
    assert decoded == data


@pytest.mark.unit
def test_encode_scalar_with_trailing_spaces_uses_quotes() -> None:
    """Test strings with leading/trailing spaces are JSON-quoted."""
    codec = ToonCodec()
    data = {"text": "  hello  "}
    toon = codec.encode(data)
    assert '"  hello  "' in toon

    decoded = codec.decode(toon)
    assert decoded == data


@pytest.mark.unit
def test_encode_scalar_with_newline_uses_quotes() -> None:
    """Test strings containing newlines are JSON-quoted."""
    codec = ToonCodec()
    data = {"multiline": "line1\nline2"}
    toon = codec.encode(data)
    # Should be JSON-encoded
    assert '"line1\\nline2"' in toon or '"line1\nline2"' in toon

    decoded = codec.decode(toon)
    assert decoded == data


@pytest.mark.unit
def test_encode_scalar_with_quote_uses_quotes() -> None:
    """Test strings containing quotes are JSON-quoted and escaped."""
    codec = ToonCodec()
    data = {"text": 'say "hello"'}
    toon = codec.encode(data)

    decoded = codec.decode(toon)
    assert decoded == data


@pytest.mark.unit
def test_decode_scalar_true() -> None:
    """Test 'true' is decoded as Python True."""
    codec = ToonCodec()
    toon = "flag: true"
    decoded = codec.decode(toon)
    assert decoded == {"flag": True}


@pytest.mark.unit
def test_decode_scalar_false() -> None:
    """Test 'false' is decoded as Python False."""
    codec = ToonCodec()
    toon = "flag: false"
    decoded = codec.decode(toon)
    assert decoded == {"flag": False}


@pytest.mark.unit
def test_decode_scalar_null() -> None:
    """Test 'null' is decoded as Python None."""
    codec = ToonCodec()
    toon = "value: null"
    decoded = codec.decode(toon)
    assert decoded == {"value": None}


@pytest.mark.unit
def test_decode_scalar_integer() -> None:
    """Test plain integers are decoded correctly."""
    codec = ToonCodec()
    toon = "count: 42"
    decoded = codec.decode(toon)
    assert decoded == {"count": 42}


@pytest.mark.unit
def test_decode_scalar_float() -> None:
    """Test plain floats are decoded correctly."""
    codec = ToonCodec()
    toon = "ratio: 3.14"
    decoded = codec.decode(toon)
    assert decoded == {"ratio": 3.14}


@pytest.mark.unit
def test_decode_scalar_empty_value_is_none() -> None:
    """Test empty value after colon is decoded as None."""
    codec = ToonCodec()
    toon = "value:"
    decoded = codec.decode(toon)
    assert decoded == {"value": None}


@pytest.mark.unit
def test_decode_invalid_scalar_line_missing_colon_raises() -> None:
    """Test that a line without colon raises ToonDecodingError."""
    codec = ToonCodec()
    bad_toon = "invalid_scalar_line"

    with pytest.raises(ToonDecodingError):
        codec.decode(bad_toon)


@pytest.mark.unit
def test_decode_invalid_scalar_line_starting_with_number_raises() -> None:
    """Test that a key starting with a number raises ToonDecodingError."""
    codec = ToonCodec()
    bad_toon = "123invalid: value"

    with pytest.raises(ToonDecodingError):
        codec.decode(bad_toon)


@pytest.mark.unit
def test_decode_scalar_with_extra_whitespace() -> None:
    """Test that extra whitespace around key and value is handled."""
    codec = ToonCodec()
    toon = "   key  :   value   "
    decoded = codec.decode(toon)
    assert decoded == {"key": "value"}


@pytest.mark.unit
def test_decode_comment_lines_ignored() -> None:
    """Test that full-line comments starting with # are ignored."""
    codec = ToonCodec()
    toon = """# This is a comment
key: value
# Another comment
"""
    decoded = codec.decode(toon)
    assert decoded == {"key": "value"}
