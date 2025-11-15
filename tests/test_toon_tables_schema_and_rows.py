from pytoon_codec import ToonCodec, ToonEncodingError, ToonDecodingError


def test_encode_decode_simple_table() -> None:
    codec = ToonCodec()

    data = {
        "metrics": [
            {"date": "2025-01-01", "value": 1},
            {"date": "2025-01-02", "value": 2},
        ]
    }

    toon = codec.encode(data)
    assert "metrics[2]{date,value}:" in toon

    decoded = codec.decode(toon)
    assert decoded == data


def test_inconsistent_row_fields_raises_encoding_error() -> None:
    codec = ToonCodec()

    data = {
        "metrics": [
            {"date": "2025-01-01", "value": 1},
            {"date": "2025-01-02"},  # missing 'value'
        ]
    }

    try:
        codec.encode(data)
    except ToonEncodingError:
        return

    assert False, "Expected ToonEncodingError for inconsistent table row schema"


def test_table_row_column_count_mismatch_raises_decoding_error() -> None:
    codec = ToonCodec()

    toon = """metrics[2]{date,value}:
  2025-01-01,1
  2025-01-02"""

    try:
        codec.decode(toon)
    except ToonDecodingError:
        return

    assert False, "Expected ToonDecodingError for mismatched number of cells in a row"


def test_table_row_count_mismatch_raises_decoding_error() -> None:
    codec = ToonCodec()

    toon = """metrics[3]{date,value}:
  2025-01-01,1
  2025-01-02,2"""

    try:
        codec.decode(toon)
    except ToonDecodingError:
        return

    assert False, "Expected ToonDecodingError for mismatched row count"
