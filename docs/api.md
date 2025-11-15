# API Reference

This document provides detailed API documentation for `pytoon-codec`.

---

## Module: `pytoon_codec`

The main module exports three public symbols:

```python
from pytoon_codec import ToonCodec, ToonEncodingError, ToonDecodingError
```

---

## Class: `ToonCodec`

The main encoder/decoder for TOON format.

### Constructor

```python
ToonCodec(*, expand_paths: bool = True)
```

**Parameters:**

- **`expand_paths`** (bool, optional): Controls dotted-path expansion during decoding.
  - When `True` (default): Dotted keys like `metadata.user.id` are expanded into nested dictionaries: `{"metadata": {"user": {"id": ...}}}`
  - When `False`: Dotted keys are preserved as flat keys: `{"metadata.user.id": ...}`

**Example:**

```python
from pytoon_codec import ToonCodec

# Default: expand dotted paths
codec = ToonCodec()

# Disable path expansion
codec_flat = ToonCodec(expand_paths=False)
```

---

### Method: `encode`

```python
encode(data: Mapping[str, Any], *, pretty_tables: bool = False) -> str
```

Encode a Python dict-like object into TOON text format. Set ``pretty_tables=True`` to indent table blocks for readability.

**Parameters:**

- **`data`** (Mapping[str, Any]): A dict or dict-like mapping containing JSON-serializable values. Must be a mapping at the top level (not a list or primitive).
- **`pretty_tables`** (bool, optional): Indent table headers/rows (arrays of objects) by two spaces.

**Returns:**

- **str**: The TOON-formatted text representation.

**Raises:**

- **`ToonEncodingError`**: When the data structure is unsupported (e.g., arrays inside nested objects, mixed-type arrays, non-homogeneous rows).
- **`TypeError`**: When `data` is not a mapping, or when unsupported Python types are encountered.

**Example:**

```python
from pytoon_codec import ToonCodec

codec = ToonCodec()

data = {
    "title": "Temperature Log",
    "readings": [
        {"time": "08:00", "temp": 20.5, "unit": "C"},
        {"time": "12:00", "temp": 24.3, "unit": "C"},
    ]
}

toon = codec.encode(data)
print(toon)
```

**Output:**

```
title: Temperature Log

readings[2]{time,temp,unit}:
  08:00,20.5,C
  12:00,24.3,C
```

**Encoding Rules:**

1. **Primitives** (str, int, float, bool, None) → `key: value`
2. **Nested objects** (dict) → Flattened into dotted keys (`user.name: Alice`)
3. **Arrays of primitives** → `key[N]: v1,v2,v3`
4. **Arrays of objects** → Tabular blocks with CSV rows

---

### Method: `decode`

```python
decode(text: str) -> dict
```

Decode TOON-formatted text back into a Python dictionary.

**Parameters:**

- **`text`** (str): A string containing TOON-formatted data.

**Returns:**

- **dict**: A dictionary representing the decoded data. Dotted keys are expanded into nested dicts if `expand_paths=True` (the default).

**Raises:**

- **`ToonDecodingError`**: When the TOON text is malformed (e.g., invalid syntax, row count mismatch, CSV parsing errors).
- **`TypeError`**: When `text` is not a string.

**Example:**

```python
from pytoon_codec import ToonCodec

codec = ToonCodec()

toon_text = """
title: User Events

events[2]{timestamp,action,user.id}:
  2024-01-15T08:00:00,login,101
  2024-01-15T17:00:00,logout,101
"""

data = codec.decode(toon_text)
print(data)
```

**Output:**

```python
{
    'title': 'User Events',
    'events': [
        {'timestamp': '2024-01-15T08:00:00', 'action': 'login', 'user': {'id': 101}},
        {'timestamp': '2024-01-15T17:00:00', 'action': 'logout', 'user': {'id': 101}}
    ]
}
```

**Decoding Rules:**

1. **Scalar lines** (`key: value`) → Primitive values
2. **Primitive arrays** (`key[N]: v1,v2`) → List of primitives
3. **Tabular blocks** (`key[N]{cols}: rows`) → List of dicts
4. **Dotted keys** (`user.id`) → Expanded to nested dicts if `expand_paths=True`

---

### Method: `decode_stream`

```python
decode_stream(text: str) -> Iterator[tuple[str, JSONValue]]
```

Iteratively yields `(key, value)` pairs as the TOON document is parsed. Keys are always returned in dotted form regardless of ``expand_paths`` so callers can build their own nested representations without buffering the entire document.

**Returns:** Iterator over `(key, value)` tuples in file order.

**Raises:** Same errors as :meth:`decode` (malformed text, duplicate keys, non-string input).

---

## Exception: `ToonEncodingError`

Raised when Python/JSON data cannot be encoded as TOON.

**Inheritance:** `Exception` → `ToonEncodingError`

**Common Causes:**

- Arrays nested inside objects or table rows
- Mixed-type arrays (e.g., `[1, "two", {"three": 3}]`)
- Non-homogeneous object arrays (rows with different field sets)
- Multi-dimensional arrays

**Example:**

```python
from pytoon_codec import ToonCodec, ToonEncodingError

codec = ToonCodec()

# This will raise ToonEncodingError: nested array inside object
data = {
    "user": {
        "name": "Alice",
        "tags": ["admin", "developer"]  # Array inside nested object
    }
}

try:
    toon = codec.encode(data)
except ToonEncodingError as e:
    print(f"Encoding failed: {e}")
```

**Workaround:**

Restructure data to lift arrays to the top level:

```python
data = {
    "user.name": "Alice",
    "tags": ["admin", "developer"]
}

toon = codec.encode(data)  # Success
```

---

## Exception: `ToonDecodingError`

Raised when TOON text cannot be decoded into valid JSON data.

**Inheritance:** `Exception` → `ToonDecodingError`

**Common Causes:**

- Malformed TOON syntax (e.g., missing colons, brackets)
- Row count mismatch (declared count ≠ actual rows)
- Column count mismatch in table rows
- Invalid CSV formatting
- Path conflicts during dotted-key expansion

**Example:**

```python
from pytoon_codec import ToonCodec, ToonDecodingError

codec = ToonCodec()

# Invalid TOON: declares 3 rows but provides only 2
toon_text = """
items[3]{id,name}:
  1,Apple
  2,Banana
"""

try:
    data = codec.decode(toon_text)
except ToonDecodingError as e:
    print(f"Decoding failed: {e}")
```

---

## TOON Format Specification

### Scalar Lines

```
key: value
```

**Examples:**

```
title: Hello World
count: 42
ratio: 3.14
active: true
notes: null
```

### Primitive Arrays

```
key[N]: value1,value2,...,valueN
```

**Examples:**

```
tags[3]: python,toon,llm
numbers[4]: 1,2,3,4
empty[0]:
```

### Tabular Arrays (Objects)

```
key[N]{field1,field2,...}:
  value1,value2,...
  value1,value2,...
```

**Example:**

```
users[2]{id,name,active}:
  1,Alice,true
  2,Bob,false
```

### Nested Objects (Dotted Keys)

Nested objects are flattened:

```python
# Python
{"user": {"profile": {"name": "Alice"}}}

# TOON
user.profile.name: Alice
```

When decoded with `expand_paths=True`, dotted keys are reconstructed into nested dicts.

### Type Literals

- **Boolean**: `true`, `false`
- **Null**: `null`
- **Numbers**: `42`, `3.14`, `-10`
- **Strings**: Unquoted if simple (no commas, quotes, or whitespace padding), otherwise JSON-quoted: `"Hello, World"`

---

## Complete Example

```python
from pytoon_codec import ToonCodec, ToonEncodingError, ToonDecodingError

codec = ToonCodec()

# Complex nested structure
data = {
    "project": "sensor-dashboard",
    "metadata": {
        "created": "2024-01-15",
        "owner": {"id": 42, "name": "Alice"}
    },
    "tags": ["iot", "sensors", "bathroom"],
    "events": [
        {
            "timestamp": "2024-01-15T08:30:00",
            "sensor": {"type": "motion", "location": "toilet"},
            "value": True
        },
        {
            "timestamp": "2024-01-15T08:35:00",
            "sensor": {"type": "door", "location": "main"},
            "value": False
        }
    ]
}

# Encode
try:
    toon = codec.encode(data)
    print(toon)
except ToonEncodingError as e:
    print(f"Cannot encode: {e}")

# Decode
try:
    decoded = codec.decode(toon)
    assert decoded == data
    print("Round-trip successful!")
except ToonDecodingError as e:
    print(f"Cannot decode: {e}")
```

**Output:**

```
project: sensor-dashboard

metadata.created: 2024-01-15

metadata.owner.id: 42

metadata.owner.name: Alice

tags[3]: iot,sensors,bathroom

events[2]{timestamp,sensor.type,sensor.location,value}:
  2024-01-15T08:30:00,motion,toilet,true
  2024-01-15T08:35:00,door,main,false

Round-trip successful!
```

---

## Advanced Usage

### Disabling Path Expansion

```python
codec = ToonCodec(expand_paths=False)

toon = """
config.db.host: localhost
config.db.port: 5432
"""

data = codec.decode(toon)
print(data)
# {'config.db.host': 'localhost', 'config.db.port': 5432}
```

Useful when you want to work with dotted keys directly without nested dicts.

---

## Type Annotations

`pytoon-codec` includes full type hints:

```python
from typing import Any, Mapping
from pytoon_codec import ToonCodec

def process_data(data: Mapping[str, Any]) -> str:
    codec = ToonCodec()
    return codec.encode(data)
```

---

## See Also

- **[Index](./index.md)**: Overview and quick start
- **[README](../README.md)**: Installation and usage examples
- **[CITATION.cff](../CITATION.cff)**: Citation metadata
