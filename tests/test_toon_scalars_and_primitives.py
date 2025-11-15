from pytoon_codec import ToonCodec, ToonDecodingError


def test_encode_decode_simple_scalars() -> None:
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


def test_encode_scalar_with_spaces_and_commas_uses_quotes() -> None:
    codec = ToonCodec()

    data = {"text": "hello, world  "}
    toon = codec.encode(data)

    # Must contain JSON-style quotes
    assert 'text: "hello, world  "' in toon

    decoded = codec.decode(toon)
    assert decoded == data


def test_decode_invalid_scalar_line_raises() -> None:
    codec = ToonCodec()

    # Missing colon
    bad_toon = "invalid_scalar_line"

    try:
        codec.decode(bad_toon)
    except ToonDecodingError:
        return

    # If we get here the error was not raised
    assert False, "Expected ToonDecodingError for invalid scalar line"
