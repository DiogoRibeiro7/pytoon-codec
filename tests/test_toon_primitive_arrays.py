from pytoon_codec import ToonCodec, ToonDecodingError


def test_encode_decode_empty_primitive_array() -> None:
    codec = ToonCodec()
    data = {"tags": []}

    toon = codec.encode(data)
    assert "tags[0]:" in toon

    decoded = codec.decode(toon)
    assert decoded == {"tags": []}


def test_encode_decode_primitive_array() -> None:
    codec = ToonCodec()
    data = {"tags": ["a", "b", "c"]}

    toon = codec.encode(data)
    assert "tags[3]:" in toon
    assert "a,b,c" in toon

    decoded = codec.decode(toon)
    assert decoded == data


def test_decode_primitive_array_length_mismatch_raises() -> None:
    codec = ToonCodec()
    bad_toon = "tags[3]: a,b"  # declares 3, only 2 values

    try:
        codec.decode(bad_toon)
    except ToonDecodingError:
        return

    assert False, "Expected ToonDecodingError for mismatched primitive array length"
