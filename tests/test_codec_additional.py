from __future__ import annotations

import pytest

from pytoon_codec import ToonCodec, ToonDecodingError, ToonEncodingError


def test_encode_requires_mapping() -> None:
    codec = ToonCodec()

    with pytest.raises(TypeError, match="mapping"):
        codec.encode(["not", "a", "mapping"])  # type: ignore[arg-type]


def test_encode_mixed_list_types_raises() -> None:
    codec = ToonCodec()

    data = {
        "mixed": [
            {"timestamp": "2025-01-01", "value": 1},
            42,
        ]
    }

    with pytest.raises(ToonEncodingError, match="mixed or unsupported element types"):
        codec.encode(data)


def test_decode_requires_string_input() -> None:
    codec = ToonCodec()

    with pytest.raises(TypeError, match="expects a string"):
        codec.decode(123)  # type: ignore[arg-type]


def test_decode_table_with_unterminated_quote_errors() -> None:
    codec = ToonCodec()
    toon = 'events[1]{name}:\n  "unterminated'

    with pytest.raises(ToonDecodingError, match="Unterminated quoted value"):
        codec.decode(toon)


def test_decode_primitive_array_with_dangling_escape_errors() -> None:
    codec = ToonCodec()
    toon = 'tags[1]: "dangling\\'

    with pytest.raises(ToonDecodingError, match="Dangling escape sequence"):
        codec.decode(toon)
