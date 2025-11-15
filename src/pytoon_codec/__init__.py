"""
pytoon-codec: A compact TOON encoder/decoder for LLM prompts.

TOON (Token-Oriented Object Notation) is a serialization format optimized for
token efficiency in LLM prompts. It encodes time-series data, nested event logs,
and structured JSON-like objects using a compact, human-readable syntax.

Key Features
------------
- Flatten nested objects into dotted keys (e.g., 'user.profile.id')
- Encode arrays of primitives inline: 'tags[3]: foo,bar,baz'
- Encode arrays of objects as tabular blocks with CSV rows
- Preserve type information for primitives (bool, null, numbers, strings)
- Reversible encoding with optional path expansion on decode

Example
-------
>>> from pytoon_codec import ToonCodec
>>> codec = ToonCodec()
>>> data = {
...     "title": "Event Log",
...     "events": [
...         {"time": "2024-01-01", "type": "login", "user": {"id": 123}},
...         {"time": "2024-01-02", "type": "logout", "user": {"id": 123}},
...     ]
... }
>>> toon = codec.encode(data)
>>> print(toon)
title: Event Log

events[2]{time,type,user.id}:
  2024-01-01,login,123
  2024-01-02,logout,123

Public API
----------
- ToonCodec: Main encoder/decoder class
- ToonEncodingError: Raised when data cannot be encoded
- ToonDecodingError: Raised when TOON text is malformed
"""

from __future__ import annotations

from .pytoon_codec import (
    ToonCodec,
    ToonDecodingError,
    ToonEncodingError,
)

__all__ = [
    "ToonCodec",
    "ToonDecodingError",
    "ToonEncodingError",
]

# Version information
try:
    from importlib.metadata import version

    __version__ = version("pytoon-codec")
except Exception:
    # Fallback if package is not installed or importlib.metadata unavailable
    __version__ = "0.2.0"
