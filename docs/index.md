# pytoon-codec Documentation

Welcome to the documentation for **pytoon-codec**, a Python library for encoding and decoding TOON (Token-Oriented Object Notation) format.

---

## What is TOON?

TOON (Token-Oriented Object Notation) is a compact serialization format optimized for embedding structured data in LLM prompts. Unlike verbose JSON, TOON represents arrays of objects as tabular blocks with CSV-style rows, automatically flattens nested objects into dotted keys, and uses a minimal syntax to preserve type information.

**Key benefits:**
- **Token efficiency**: Reduces token count by 30-50% compared to JSON for time-series and event logs
- **Human-readable**: Clean tabular structure that's easy to scan and edit
- **Type-safe**: Preserves JSON types (bool, null, numbers, strings)
- **Reversible**: Full round-trip conversion between JSON and TOON

---

## Overview

`pytoon-codec` provides a simple Python API for working with TOON format:

```python
from pytoon_codec import ToonCodec

codec = ToonCodec()

# Encode Python data to TOON
data = {
    "title": "Sales Metrics",
    "metrics": [
        {"date": "2024-01-01", "revenue": 1250.50, "units": 42},
        {"date": "2024-01-02", "revenue": 1340.75, "units": 51},
    ]
}

toon = codec.encode(data)
print(toon)
```

**Output:**

```
title: Sales Metrics

metrics[2]{date,revenue,units}:
  2024-01-01,1250.5,42
  2024-01-02,1340.75,51
```

**Decode back to Python:**

```python
decoded = codec.decode(toon)
assert decoded == data
```

---

## Core Features

### 1. Tabular Arrays

Arrays of objects are encoded as tabular blocks:

```python
# Input
events = [
    {"time": "08:00", "event": "start"},
    {"time": "17:00", "event": "end"}
]

# TOON output
events[2]{time,event}:
  08:00,start
  17:00,end
```

### 2. Dotted Keys for Nested Objects

Nested structures are automatically flattened:

```python
# Input
user = {"profile": {"name": "Alice", "age": 30}}

# TOON output
user.profile.name: Alice
user.profile.age: 30
```

### 3. Type Preservation

All JSON types are preserved:

```python
# Input
data = {"flag": True, "count": 42, "ratio": 3.14, "empty": None}

# TOON output
flag: true
count: 42
ratio: 3.14
empty: null
```

---

## Quick Start

### Installation

```bash
pip install pytoon-codec
```

or with Poetry:

```bash
poetry add pytoon-codec
```

### Basic Usage

```python
from pytoon_codec import ToonCodec

codec = ToonCodec()

# Encode
data = {"name": "Test", "values": [1, 2, 3]}
toon = codec.encode(data)

# Decode
decoded = codec.decode(toon)
```

---

## Documentation Index

- **[API Reference](./api.md)**: Detailed API documentation
- **[README](../README.md)**: Full usage examples and installation guide

---

## Use Cases

`pytoon-codec` is particularly well-suited for:

- **LLM prompt engineering**: Embedding time-series data, logs, or structured context in prompts
- **Data serialization**: Compact representation for analytics dashboards, metrics, event streams
- **Human-readable logs**: More scannable than JSON for tabular data
- **Token budget optimization**: When working with token-limited APIs

---

## Design Philosophy

TOON is designed with intentional constraints to maintain simplicity and token efficiency:

- Top-level value must be a dict
- Arrays must be homogeneous (all primitives or all objects)
- No arrays inside nested objects or tabular rows
- No mixed-type arrays or multi-dimensional arrays

These constraints ensure TOON remains compact, predictable, and optimized for common time-series and event-log patterns.

For more complex data structures, consider restructuring or using JSON for those portions.

---

## Support & Contributing

- **GitHub**: [DiogoRibeiro7/pytoon-codec](https://github.com/DiogoRibeiro7/pytoon-codec)
- **Issues**: [Report bugs or request features](https://github.com/DiogoRibeiro7/pytoon-codec/issues)
- **Contributing**: Pull requests welcome!

---

## License

MIT License. See [LICENSE](../LICENSE) for details.
