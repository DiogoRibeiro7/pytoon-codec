# pytoon-codec

[![CI](https://github.com/DiogoRibeiro7/pytoon-codec/actions/workflows/ci.yml/badge.svg)](https://github.com/DiogoRibeiro7/pytoon-codec/actions/workflows/ci.yml)
[![License: MIT](https://img.shields.io/github/license/DiogoRibeiro7/pytoon-codec.svg)](https://github.com/DiogoRibeiro7/pytoon-codec/blob/main/LICENSE)
[![Python Versions](https://img.shields.io/badge/python-3.10%20%7C%203.11%20%7C%203.12-blue)](pyproject.toml)
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17619909.svg)](https://doi.org/10.5281/zenodo.17619909)

**pytoon-codec** is a Python library that implements a TOON (Token-Oriented Object Notation) encoder/decoder for time-series data, nested event logs, and structured JSON-like objects. TOON is designed to maximize token efficiency when embedding structured data in LLM prompts, using a compact, human-readable syntax that represents arrays of objects as tabular blocks with CSV-style rows, flattens nested objects into dotted keys, and preserves type information for primitives.

---

## Features

- **Time-series encoding**: Represent arrays of homogeneous objects as compact tabular blocks with column headers and CSV rows
- **Nested event encoding**: Automatically flatten nested objects (e.g., `user.id`, `payload.sensor`) into dotted column names
- **Round-trip JSON � TOON**: Full bidirectional conversion with optional dotted-path expansion on decode
- **Type preservation**: Maintains JSON types (bool, null, numbers, strings) with clear literal syntax
- **Token efficiency**: Optimized for minimal token usage in LLM prompts compared to verbose JSON
- **Human-readable**: Clean, structured format that's easy to read and edit manually

---

## Installation

### Using Poetry (recommended for development)

```bash
poetry add pytoon-codec
```

### Using pip

```bash
pip install pytoon-codec
```

---

## Usage Examples

### Basic Time-Series Example

Encode a simple metrics time series:

```python
from pytoon_codec import ToonCodec

codec = ToonCodec()

data = {
    "project": "analytics-dashboard",
    "metrics": [
        {"date": "2024-01-01", "views": 1250, "clicks": 89},
        {"date": "2024-01-02", "views": 1340, "clicks": 102},
        {"date": "2024-01-03", "views": 1180, "clicks": 76},
    ]
}

toon = codec.encode(data)
print(toon)
```

**Output:**

```
project: analytics-dashboard

metrics[3]{date,views,clicks}:
  2024-01-01,1250,89
  2024-01-02,1340,102
  2024-01-03,1180,76
```

**Decode it back:**

```python
decoded = codec.decode(toon)
# Returns the original nested structure
assert decoded == data
```

---

## Examples

- `examples/time_series_basic.py` – encodes/decodes a metric time series.
  ```bash
  poetry run python examples/time_series_basic.py
  ```
- `examples/nested_events_basic.py` – encodes/decodes nested sensor events.
  ```bash
  poetry run python examples/nested_events_basic.py
  ```
- Interactive walkthrough: see [`examples/notebooks/pytoon_codec_intro.ipynb`](examples/notebooks/pytoon_codec_intro.ipynb) and the setup notes in [`examples/notebooks/README.md`](examples/notebooks/README.md).

---

## Benchmarking

Quick CPU benchmarks are located under `benchmarks/`. Run them after installing dependencies:

```bash
poetry run python benchmarks/benchmark_toon_codec.py
```

These measurements are intended to catch obvious encode/decode regressions for medium-sized time series and event logs between releases (they are not tuned to compete with highly optimized C/C++ serializers).

---

## LLM integration

A common workflow is:

1. Build a Python dict containing metrics/events.
2. Encode it to TOON (`codec.encode(data)`) and embed the resulting block into the LLM prompt.
3. Let the LLM return either prose (interpreting the data) or another TOON block (for structured responses).
4. Decode any TOON replies back into Python dicts with `codec.decode(...)`.

See:

- [`examples/llm_integration_openai.py`](examples/llm_integration_openai.py) – encodes a payload and shows a commented OpenAI client call. Install `openai` and set `OPENAI_API_KEY` before actually invoking the API.
- [`examples/llm_integration_generic.py`](examples/llm_integration_generic.py) – demonstrates the same flow with a `call_llm()` placeholder, highlighting that TOON is just a serialization layer before/after any LLM provider.

---

## API quick reference

```python
from pytoon_codec import ToonCodec, ToonEncodingError, ToonDecodingError
```

- `ToonCodec`: main encoder/decoder with `encode()`/`decode()` helpers and optional dotted-path expansion when decoding.
- `ToonEncodingError`: raised when the input structure cannot be represented in TOON (e.g., nested arrays inside objects, mixed row schemas).
- `ToonDecodingError`: raised when TOON text is malformed (e.g., row-length mismatches, invalid quoting, duplicate keys).

---

### Nested Events with Dotted Columns

When your events have nested objects (e.g., user info, payload), TOON flattens them into dotted column names:

```python
from pytoon_codec import ToonCodec

codec = ToonCodec()

data = {
    "log_title": "Bathroom Sensor Events",
    "events": [
        {
            "timestamp": "2024-01-15T08:30:00",
            "type": "motion",
            "payload": {"sensor": "toilet", "room": "bathroom"},
            "user": {"id": 123, "name": "Alice"}
        },
        {
            "timestamp": "2024-01-15T08:35:00",
            "type": "door",
            "payload": {"sensor": "main_door", "room": "bathroom"},
            "user": {"id": 123, "name": "Alice"}
        },
    ]
}

toon = codec.encode(data)
print(toon)
```

**Output:**

```
log_title: Bathroom Sensor Events

events[2]{timestamp,type,payload.sensor,payload.room,user.id,user.name}:
  2024-01-15T08:30:00,motion,toilet,bathroom,123,Alice
  2024-01-15T08:35:00,door,main_door,bathroom,123,Alice
```

The dotted keys (`payload.sensor`, `user.id`) are automatically expanded back into nested dicts when decoding.

---

### Disabling Path Expansion

By default, `ToonCodec` expands dotted keys like `user.id` back into nested dicts on decode. You can disable this:

```python
from pytoon_codec import ToonCodec

codec = ToonCodec(expand_paths=False)

toon = """
metadata.user.id: 42
metadata.user.name: Bob
"""

decoded = codec.decode(toon)
print(decoded)
# {'metadata.user.id': 42, 'metadata.user.name': 'Bob'}
```

With `expand_paths=True` (the default), you'd get:

```python
codec = ToonCodec(expand_paths=True)
decoded = codec.decode(toon)
print(decoded)
# {'metadata': {'user': {'id': 42, 'name': 'Bob'}}}
```

---

### Handling Primitives and Edge Cases

```python
from pytoon_codec import ToonCodec

codec = ToonCodec()

data = {
    "title": "Edge Cases Demo",
    "active": True,
    "count": 42,
    "ratio": 3.14,
    "notes": None,
    "tags": ["python", "toon", "llm"],
    "empty_list": []
}

toon = codec.encode(data)
print(toon)
```

**Output:**

```
title: Edge Cases Demo

active: true

count: 42

ratio: 3.14

notes: null

tags[3]: python,toon,llm

empty_list[0]:
```

---

## Design Constraints & Limitations

`pytoon-codec` is optimized for common time-series and event-log patterns. The following constraints apply:

- **Top-level must be a mapping**: The root value must be a dict-like object
- **Homogeneous arrays**: Arrays of objects must have consistent field sets across all rows
- **No nested arrays in objects**: Arrays inside nested objects or tabular rows are not supported (will raise `ToonEncodingError`)
- **No mixed-type arrays**: Arrays must contain either all primitives or all objects, not a mix
- **No arrays of arrays**: Multi-dimensional arrays are not supported

For data that doesn't fit these constraints, consider:
- Restructuring to lift arrays to the top level
- Encoding that portion as raw JSON
- Using a different serialization format

These constraints are intentional to maintain TOON's compact, tabular structure optimized for LLM token efficiency.

---

## API Reference

### `ToonCodec`

Main encoder/decoder class.

**Constructor:**
```python
ToonCodec(expand_paths: bool = True)
```
- `expand_paths`: When `True`, dotted keys like `user.id` are expanded into nested dicts on decode. When `False`, they remain as flat keys.

**Methods:**

- `encode(data: Mapping[str, Any]) -> str`: Encode a dict-like object into TOON text
- `decode(text: str) -> dict`: Decode TOON text back into a dict

**Exceptions:**

- `ToonEncodingError`: Raised when data cannot be encoded (e.g., unsupported structure)
- `ToonDecodingError`: Raised when TOON text is malformed

---

## Releases and Versioning

This project follows [Semantic Versioning](https://semver.org/) (SemVer). Releases are tagged as `vX.Y.Z` (e.g., `v0.2.0`, `v0.2.1`).

### Release History

See [CHANGELOG.md](./CHANGELOG.md) for a detailed history of changes in each release.

### Creating a Release

If you're a maintainer, see [RELEASING.md](./RELEASING.md) for the step-by-step release process, including:
- Version bumping across all files
- Quality checks and testing
- Building and publishing to PyPI
- Git tagging and Zenodo archiving

---

## Citing this software

If you use `pytoon-codec` in your research or project, please cite it using the metadata provided in [`CITATION.cff`](./CITATION.cff).

### Zenodo DOI

[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.17619909.svg)](https://doi.org/10.5281/zenodo.17619909)

The published Zenodo record for `pytoon-codec` lives at [doi.org/10.5281/zenodo.17619909](https://doi.org/10.5281/zenodo.17619909), providing a permanent, citable reference for this repository.

### BibTeX

```bibtex
@software{ribeiro2025pytoon,
  author = {Ribeiro, Diogo},
  title = {pytoon-codec: TOON encoder/decoder for time series and events},
  year = {2025},
  url = {https://github.com/DiogoRibeiro7/pytoon-codec},
  version = {0.2.0}
}
```

### Citation File Format (CFF)

This repository includes a `CITATION.cff` file with complete metadata. You can use tools like [cffinit](https://citation-file-format.github.io/) to convert it to other citation formats.

---

## Contributing

Contributions are welcome! Please open an issue or pull request on [GitHub](https://github.com/DiogoRibeiro7/pytoon-codec).

---

## License

MIT License. See [LICENSE](./LICENSE) for details.

---

## Links

- **GitHub**: https://github.com/DiogoRibeiro7/pytoon-codec
- **Documentation**: See [`docs/`](./docs/)
- **PyPI**: *(coming soon)*
