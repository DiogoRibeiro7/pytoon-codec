from pytoon_codec import ToonCodec, ToonEncodingError


def test_encode_decode_nested_object_flatten_expand() -> None:
    codec = ToonCodec(expand_paths=True)

    data = {
        "metadata": {
            "user": {"id": "u-1", "role": "admin"},
            "source": "test",
        }
    }

    toon = codec.encode(data)

    # Check flattening
    assert "metadata.user.id:" in toon or "metadata.user.id" in toon
    assert "metadata.user.role:" in toon or "metadata.user.role" in toon

    decoded = codec.decode(toon)
    assert decoded == data


def test_flatten_nested_arrays_in_object_raise_encoding_error() -> None:
    codec = ToonCodec()

    data = {
        "metadata": {
            "tags": ["a", "b", "c"],  # array inside nested object: unsupported
        }
    }

    try:
        codec.encode(data)
    except ToonEncodingError:
        return

    assert False, "Expected ToonEncodingError for array nested inside object"


def test_decode_without_expand_paths_keeps_flat_keys() -> None:
    codec = ToonCodec(expand_paths=False)

    toon = """metadata.user.id: u-1
metadata.user.role: admin
"""

    decoded = codec.decode(toon)

    assert decoded == {
        "metadata.user.id": "u-1",
        "metadata.user.role": "admin",
    }
