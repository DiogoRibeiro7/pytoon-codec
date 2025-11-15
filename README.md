# pytoon-codec

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

This project follows [Semantic Versioning](https://semver.org/) (SemVer). Releases are tagged as `vX.Y.Z` (e.g., `v0.1.0`, `v0.2.0`).

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

<!--
Once the first GitHub release is archived by Zenodo, a DOI badge will be available here.
Replace XXXXXXX below with the actual Zenodo DOI after the first release is archived.
-->

<!--
[![DOI](https://zenodo.org/badge/DOI/10.5281/zenodo.XXXXXXX.svg)](https://doi.org/10.5281/zenodo.XXXXXXX)
-->

A Zenodo DOI will be automatically generated when the first GitHub release is created and archived. This DOI provides a permanent, citable reference to the software.

### BibTeX

```bibtex
@software{ribeiro2025pytoon,
  author = {Ribeiro, Diogo},
  title = {pytoon-codec: TOON encoder/decoder for time series and events},
  year = {2025},
  url = {https://github.com/DiogoRibeiro7/pytoon-codec},
  version = {0.1.0}
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
