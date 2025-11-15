"""
Regression tests for string formatting and quoting behavior.

These tests ensure specific edge cases and bugs that were fixed remain fixed.
"""

import pytest

from pytoon_codec import ToonCodec


@pytest.mark.regression
def test_regression_string_with_comma_and_spaces_roundtrip() -> None:
    """
    Regression: Ensure strings with commas and trailing spaces are quoted
    and roundtrip correctly without data loss.

    Bug: Early versions didn't properly quote strings with trailing spaces,
    causing them to be trimmed during decode.
    """
    codec = ToonCodec()

    data = {"text": "hello, world  "}
    toon = codec.encode(data)

    # Should be JSON-quoted
    assert '"hello, world  "' in toon

    decoded = codec.decode(toon)
    assert decoded == data
    assert decoded["text"] == "hello, world  "  # Verify spaces preserved


@pytest.mark.regression
def test_regression_table_with_special_characters_in_strings() -> None:
    """
    Regression: Ensure table cells with commas/newlines are quoted and preserved.

    Bug: CSV cells with special characters weren't being properly escaped in
    early implementations, causing parse errors or data corruption.
    """
    codec = ToonCodec()

    data = {
        "events": [
            {
                "ts": "2025-01-01T00:00:00Z",
                "msg": "Hello, world",  # includes comma
            },
            {
                "ts": "2025-01-01T01:00:00Z",
                "msg": "Line1\nLine2",  # includes newline
            },
        ]
    }

    toon = codec.encode(data)
    decoded = codec.decode(toon)

    assert decoded == data
    assert decoded["events"][0]["msg"] == "Hello, world"
    assert decoded["events"][1]["msg"] == "Line1\nLine2"


@pytest.mark.regression
def test_regression_empty_string_roundtrip() -> None:
    """
    Regression: Ensure empty strings are preserved and not confused with None.

    Bug: Empty strings were being decoded as None in some cases.
    """
    codec = ToonCodec()

    data = {"empty": "", "nonempty": "value"}
    toon = codec.encode(data)
    decoded = codec.decode(toon)

    assert decoded["empty"] == ""
    assert decoded["nonempty"] == "value"


@pytest.mark.regression
def test_regression_string_containing_only_spaces() -> None:
    """
    Regression: Strings containing only spaces should be quoted and preserved.

    Bug: Strings like "   " were being trimmed to empty strings.
    """
    codec = ToonCodec()

    data = {"spaces": "   "}
    toon = codec.encode(data)

    # Should be quoted
    assert '"   "' in toon

    decoded = codec.decode(toon)
    assert decoded["spaces"] == "   "


@pytest.mark.regression
def test_regression_string_with_colon() -> None:
    """
    Regression: Strings containing colons should not break parsing.

    Bug: Unquoted strings with colons could confuse the key:value parser.
    """
    codec = ToonCodec()

    data = {"url": "http://example.com:8080"}
    toon = codec.encode(data)
    decoded = codec.decode(toon)

    assert decoded["url"] == "http://example.com:8080"


@pytest.mark.regression
def test_regression_numeric_string_vs_number() -> None:
    """
    Regression: Ensure numeric strings are preserved as strings when quoted.

    Bug: The string "123" was sometimes decoded as integer 123.
    """
    codec = ToonCodec()

    # Quoted numeric string should remain a string
    toon = 'id: "123"'
    decoded = codec.decode(toon)
    assert decoded["id"] == "123"
    assert isinstance(decoded["id"], str)

    # Unquoted should be parsed as int
    toon2 = "count: 123"
    decoded2 = codec.decode(toon2)
    assert decoded2["count"] == 123
    assert isinstance(decoded2["count"], int)


@pytest.mark.regression
def test_regression_boolean_string_vs_boolean() -> None:
    """
    Regression: Ensure quoted "true"/"false" are strings, not booleans.

    Bug: Quoted boolean literals were being decoded as booleans.
    """
    codec = ToonCodec()

    # Quoted should be strings
    toon = 'flag: "true"'
    decoded = codec.decode(toon)
    assert decoded["flag"] == "true"
    assert isinstance(decoded["flag"], str)

    # Unquoted should be boolean
    toon2 = "flag: true"
    decoded2 = codec.decode(toon2)
    assert decoded2["flag"] is True
    assert isinstance(decoded2["flag"], bool)


@pytest.mark.regression
def test_regression_table_cell_with_quote_and_comma() -> None:
    """
    Regression: Table cells with both quotes and commas must be properly escaped.

    Bug: Complex escaping scenarios weren't handled correctly.
    """
    codec = ToonCodec()

    data = {
        "items": [
            {"id": 1, "desc": 'Product: "Best, #1"'},
            {"id": 2, "desc": 'Item with "quotes" and, commas'},
        ]
    }

    toon = codec.encode(data)
    decoded = codec.decode(toon)

    assert decoded == data


@pytest.mark.regression
def test_regression_unicode_characters_preserved() -> None:
    """
    Regression: Ensure Unicode characters are preserved correctly.

    Bug: Non-ASCII characters were sometimes corrupted or lost.
    """
    codec = ToonCodec()

    data = {"message": "Hello 世界 🌍", "emoji": "😀👍", "accents": "café résumé"}

    toon = codec.encode(data)
    decoded = codec.decode(toon)

    assert decoded == data
