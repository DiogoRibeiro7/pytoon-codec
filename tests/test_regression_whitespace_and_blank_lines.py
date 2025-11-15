from pytoon_codec import ToonCodec


def test_regression_ignore_blank_lines_between_blocks() -> None:
    """
    Ensure blank lines between blocks do not affect decoding.
    """
    codec = ToonCodec()

    toon = """version: 1

metrics[2]{date,value}:
  2025-01-01,1
  2025-01-02,2

"""

    decoded = codec.decode(toon)

    assert decoded == {
        "version": 1,
        "metrics": [
            {"date": "2025-01-01", "value": 1},
            {"date": "2025-01-02", "value": 2},
        ],
    }


def test_regression_ignore_blank_lines_inside_table() -> None:
    """
    Ensure blank lines inside a table block are ignored.
    """
    codec = ToonCodec()

    toon = """metrics[2]{date,value}:
  2025-01-01,1

  2025-01-02,2
"""

    decoded = codec.decode(toon)

    assert decoded == {
        "metrics": [
            {"date": "2025-01-01", "value": 1},
            {"date": "2025-01-02", "value": 2},
        ],
    }
