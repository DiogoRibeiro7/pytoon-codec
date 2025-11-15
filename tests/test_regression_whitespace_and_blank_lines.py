"""
Regression tests for whitespace and blank line handling.

These tests ensure specific edge cases around whitespace parsing remain fixed.
"""

import pytest

from pytoon_codec import ToonCodec


@pytest.mark.regression
def test_regression_ignore_blank_lines_between_blocks() -> None:
    """
    Regression: Ensure blank lines between top-level blocks do not affect decoding.

    Bug: Early versions would fail or produce incorrect results when
    multiple blank lines appeared between blocks.
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


@pytest.mark.regression
def test_regression_ignore_blank_lines_inside_table() -> None:
    """
    Regression: Ensure blank lines inside a table block are properly ignored.

    Bug: Blank lines within table bodies were being counted as rows,
    causing row count mismatches.
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


@pytest.mark.regression
def test_regression_multiple_blank_lines_inside_table() -> None:
    """
    Regression: Multiple consecutive blank lines in table should be ignored.

    Bug: Multiple blank lines could cause parser state issues.
    """
    codec = ToonCodec()

    toon = """events[3]{id,type}:
  1,start


  2,middle

  3,end
"""

    decoded = codec.decode(toon)

    assert len(decoded["events"]) == 3
    assert decoded["events"][0]["id"] == 1
    assert decoded["events"][1]["id"] == 2
    assert decoded["events"][2]["id"] == 3


@pytest.mark.regression
def test_regression_leading_and_trailing_whitespace_in_document() -> None:
    """
    Regression: Leading/trailing blank lines in document should be ignored.

    Bug: Document with leading/trailing blank lines would fail to parse.
    """
    codec = ToonCodec()

    toon = """

version: 1
name: test

"""

    decoded = codec.decode(toon)

    assert decoded == {"version": 1, "name": "test"}


@pytest.mark.regression
def test_regression_tabs_vs_spaces_in_table_indentation() -> None:
    """
    Regression: Table rows with mixed tabs/spaces indentation should work.

    Bug: Parser was sensitive to exact whitespace character used for indentation.
    """
    codec = ToonCodec()

    # Using spaces for indentation
    toon = """items[2]{id,name}:
  1,Alice
  2,Bob
"""

    decoded = codec.decode(toon)
    assert len(decoded["items"]) == 2


@pytest.mark.regression
def test_regression_varying_indentation_levels() -> None:
    """
    Regression: Table rows can have varying amounts of indentation.

    Bug: Parser required exact indentation matching.
    """
    codec = ToonCodec()

    toon = """items[3]{id,name}:
  1,Alice
    2,Bob
      3,Charlie
"""

    decoded = codec.decode(toon)

    # All rows should be parsed despite different indentation
    assert len(decoded["items"]) == 3
    assert decoded["items"][0]["name"] == "Alice"
    assert decoded["items"][1]["name"] == "Bob"
    assert decoded["items"][2]["name"] == "Charlie"


@pytest.mark.regression
def test_regression_whitespace_only_lines_ignored() -> None:
    """
    Regression: Lines containing only whitespace should be treated as blank.

    Bug: Lines with only spaces/tabs were not recognized as blank lines.
    """
    codec = ToonCodec()

    toon = """version: 1

metrics[1]{value}:
  100
"""

    decoded = codec.decode(toon)

    assert decoded == {"version": 1, "metrics": [{"value": 100}]}


@pytest.mark.regression
def test_regression_windows_line_endings() -> None:
    """
    Regression: Windows-style line endings (\\r\\n) should be handled correctly.

    Bug: \\r characters were causing parsing issues.
    """
    codec = ToonCodec()

    # Simulate Windows line endings
    toon = "version: 1\r\nname: test\r\n"

    decoded = codec.decode(toon)

    assert decoded == {"version": 1, "name": "test"}


@pytest.mark.regression
def test_regression_mixed_line_endings() -> None:
    """
    Regression: Mixed Unix (\\n) and Windows (\\r\\n) line endings should work.

    Bug: Inconsistent line endings caused parser errors.
    """
    codec = ToonCodec()

    toon = "version: 1\r\nname: test\ntags[2]: a,b\r\n"

    decoded = codec.decode(toon)

    assert decoded == {"version": 1, "name": "test", "tags": ["a", "b"]}


@pytest.mark.regression
def test_regression_preserve_internal_whitespace_in_values() -> None:
    """
    Regression: Internal whitespace in unquoted values should be preserved.

    Bug: Internal spaces were being collapsed or removed.
    """
    codec = ToonCodec()

    # Note: For strings with internal spaces to be unquoted,
    # they must not have leading/trailing spaces or commas
    toon = "name: Alice Smith"

    decoded = codec.decode(toon)

    # Should preserve the space between first and last name
    assert decoded["name"] == "Alice Smith"
