"""
Unit tests for primitive array encoding/decoding.
"""

import pytest

from pytoon_codec import ToonCodec, ToonDecodingError


@pytest.mark.unit
def test_encode_decode_empty_primitive_array() -> None:
    """Test empty arrays are encoded as key[0]:"""
    codec = ToonCodec()
    data = {"tags": []}

    toon = codec.encode(data)
    assert "tags[0]:" in toon

    decoded = codec.decode(toon)
    assert decoded == {"tags": []}


@pytest.mark.unit
def test_encode_decode_primitive_string_array() -> None:
    """Test array of strings is encoded inline with commas."""
    codec = ToonCodec()
    data = {"tags": ["python", "toon", "llm"]}

    toon = codec.encode(data)
    assert "tags[3]:" in toon
    assert "python,toon,llm" in toon

    decoded = codec.decode(toon)
    assert decoded == data


@pytest.mark.unit
def test_encode_decode_primitive_int_array() -> None:
    """Test array of integers is encoded correctly."""
    codec = ToonCodec()
    data = {"numbers": [1, 2, 3, 4]}

    toon = codec.encode(data)
    assert "numbers[4]:" in toon
    assert "1,2,3,4" in toon

    decoded = codec.decode(toon)
    assert decoded == data


@pytest.mark.unit
def test_encode_decode_primitive_float_array() -> None:
    """Test array of floats is encoded correctly."""
    codec = ToonCodec()
    data = {"values": [1.5, 2.7, 3.14]}

    toon = codec.encode(data)
    assert "values[3]:" in toon

    decoded = codec.decode(toon)
    assert decoded == data


@pytest.mark.unit
def test_encode_decode_primitive_bool_array() -> None:
    """Test array of booleans is encoded as true/false."""
    codec = ToonCodec()
    data = {"flags": [True, False, True]}

    toon = codec.encode(data)
    assert "flags[3]:" in toon
    assert "true,false,true" in toon

    decoded = codec.decode(toon)
    assert decoded == data


@pytest.mark.unit
def test_encode_decode_primitive_mixed_types_array() -> None:
    """Test array with mixed primitive types (str, int, bool, None)."""
    codec = ToonCodec()
    data = {"mixed": ["hello", 42, True, None]}

    toon = codec.encode(data)
    assert "mixed[4]:" in toon

    decoded = codec.decode(toon)
    assert decoded == data


@pytest.mark.unit
def test_encode_primitive_array_with_special_strings() -> None:
    """Test array containing strings that need quoting."""
    codec = ToonCodec()
    data = {"items": ["hello, world", "foo", "bar baz"]}

    toon = codec.encode(data)

    decoded = codec.decode(toon)
    assert decoded == data


@pytest.mark.unit
def test_decode_primitive_array_single_item() -> None:
    """Test decoding array with single item."""
    codec = ToonCodec()
    toon = "tags[1]: foo"

    decoded = codec.decode(toon)
    assert decoded == {"tags": ["foo"]}


@pytest.mark.unit
def test_decode_primitive_array_empty() -> None:
    """Test decoding empty array."""
    codec = ToonCodec()
    toon = "tags[0]:"

    decoded = codec.decode(toon)
    assert decoded == {"tags": []}


@pytest.mark.unit
def test_decode_primitive_array_with_whitespace() -> None:
    """Test decoding handles extra whitespace gracefully."""
    codec = ToonCodec()
    toon = "tags[3]:  foo , bar , baz  "

    decoded = codec.decode(toon)
    # CSV parsing will strip spaces from unquoted values
    assert decoded == {"tags": ["foo", "bar", "baz"]}


@pytest.mark.unit
def test_decode_primitive_array_length_mismatch_too_few_raises() -> None:
    """Test that declaring more items than provided raises ToonDecodingError."""
    codec = ToonCodec()
    bad_toon = "tags[5]: a,b,c"  # declares 5, only 3 values

    with pytest.raises(ToonDecodingError, match="declares length 5"):
        codec.decode(bad_toon)


@pytest.mark.unit
def test_decode_primitive_array_length_mismatch_too_many_raises() -> None:
    """Test that providing more items than declared raises ToonDecodingError."""
    codec = ToonCodec()
    bad_toon = "tags[2]: a,b,c,d"  # declares 2, but 4 values

    with pytest.raises(ToonDecodingError, match="declares length 2"):
        codec.decode(bad_toon)


@pytest.mark.unit
def test_decode_primitive_array_zero_length_with_values_raises() -> None:
    """Test that empty array declaration with values raises error."""
    codec = ToonCodec()
    bad_toon = "tags[0]: a,b"  # declares 0 but has values

    with pytest.raises(ToonDecodingError):
        codec.decode(bad_toon)


@pytest.mark.unit
def test_decode_primitive_array_type_inference() -> None:
    """Test that type inference works correctly for array values."""
    codec = ToonCodec()
    toon = "data[6]: 42,3.14,true,false,null,hello"

    decoded = codec.decode(toon)
    assert decoded == {"data": [42, 3.14, True, False, None, "hello"]}


@pytest.mark.unit
def test_decode_primitive_array_quoted_strings() -> None:
    """Test decoding array with JSON-quoted strings."""
    codec = ToonCodec()
    toon = 'items[2]: "hello, world","foo"'

    decoded = codec.decode(toon)
    assert decoded == {"items": ["hello, world", "foo"]}
