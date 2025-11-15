from pytoon_codec import ToonCodec


def test_regression_string_with_comma_and_spaces_roundtrip() -> None:
    """
    Ensure strings with commas and trailing spaces are quoted and roundtrip correctly.
    """
    codec = ToonCodec()

    data = {"text": "hello, world  "}
    toon = codec.encode(data)
    decoded = codec.decode(toon)

    assert decoded == data


def test_regression_table_with_special_characters_in_strings() -> None:
    """
    Ensure table cells with commas/newlines are quoted and preserved.
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
