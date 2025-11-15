from __future__ import annotations

import json
import re
from collections.abc import Iterable, Mapping, MutableMapping, Sequence
from dataclasses import dataclass
from typing import Any, Iterator, TypeAlias, cast

JSONPrimitive = str | int | float | bool | None
JSONValue: TypeAlias = JSONPrimitive | list["JSONValue"] | dict[str, "JSONValue"]
JSONList: TypeAlias = list[JSONValue]
JSONDict: TypeAlias = dict[str, JSONValue]


class ToonEncodingError(Exception):
    """Raised when Python/JSON data cannot be encoded as TOON."""

    pass


class ToonDecodingError(Exception):
    """Raised when TOON text cannot be decoded into JSON data."""

    pass


@dataclass
class ToonTableSchema:
    """
    Schema for a TOON table block.

    Attributes:
        name: Logical table name (e.g. 'metrics', 'events').
        field_names: Ordered column names for each row.
        n_rows: Number of rows declared in the header.
    """

    name: str
    field_names: list[str]
    n_rows: int


class ToonCodec:
    """
    Compact TOON encoder/decoder tuned for time-series and event logs.

    Design choices
    --------------
    * Top-level value must be a mapping (dict-like).
    * Values may be:
        - JSON primitives                 -> 'key: value'
        - dict (nested object)            -> flattened into dotted keys
        - list of primitives              -> 'key[N]: v1,v2,...'
        - list of (possibly nested) dicts -> tabular block 'key[N]{cols}: ...'
    * Nested objects inside rows are flattened into dotted column names
      (e.g. 'payload.sensor', 'user.id'), following TOON's key-folding idea.

    This covers:
        - metrics time series like metrics[5]{date,views,...}: ...
        - nested event logs where each event has a payload/context object.

    Unsupported (for now)
    ---------------------
    * Arrays of arrays
    * Lists with a mix of primitives and objects
    * Objects that contain arrays apart from the top-level uniform lists

    In those cases, ToonEncodingError is raised so callers can fall back
    to raw JSON if needed.
    """

    # ------------------------------------------------------------------
    # Construction
    # ------------------------------------------------------------------

    def __init__(self, *, expand_paths: bool = True) -> None:
        """
        Args:
            expand_paths:
                When True, `decode()` expands dotted keys like
                'metadata.user.id' back into nested dictionaries.
                When False, dotted keys are left as flat keys.
        """
        self.expand_paths = expand_paths

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def encode(self, data: Mapping[str, Any], *, pretty_tables: bool = False) -> str:
        """
        Encode a JSON-like mapping into TOON text.

        Supported shapes:
            * Top-level mappings only (not lists/primitives)
            * Primitives -> ``key: value``
            * Nested dicts -> flattened dotted keys
            * Lists of primitives -> ``key[N]: v1,v2``
            * Lists of dicts -> tabular blocks ``key[N]{cols}: ...``

        Example:
            >>> codec = ToonCodec()
            >>> codec.encode({"stats": [{"date": "2025-01-01", "views": 42}]})
            'stats[1]{date,views}:\\n  2025-01-01,42'

        Args:
            data:
                Mapping from top-level keys to JSON-serializable values.
            pretty_tables:
                When True, table blocks (arrays of objects) are indented by
                two spaces to improve readability.

        Returns:
            str: TOON representation.

        Raises:
            ToonEncodingError: if the structure violates the supported shapes
                (e.g., arrays nested inside objects or heterogeneous rows).
            TypeError: if the top-level value is not a mapping or primitives
                contain unsupported Python types.
        """
        if not isinstance(data, Mapping):
            raise TypeError(f"ToonCodec.encode expects a mapping, got {type(data)}")

        blocks: list[str] = []

        # Preserve original key order
        for key, value in data.items():
            block_lines = self._encode_field(
                key,
                value,
                indent=0,
                pretty_tables=pretty_tables,
            )
            if block_lines:
                blocks.append("\n".join(block_lines))

        return "\n\n".join(blocks)

    def decode(self, text: str) -> JSONDict:
        """
        Decode TOON text back into JSON-like data produced by :meth:`encode`.

        Supported constructs:
            * Scalar lines       -> ``key: primitive``
            * Primitive arrays   -> ``key[N]: v1,v2,...``
            * Tabular arrays     -> ``key[N]{cols}: <rows>``

        Example:
            >>> codec = ToonCodec()
            >>> codec.decode('flag: true')
            {'flag': True}

        Args:
            text: TOON document as a string.

        Returns:
            dict[str, Any]: Mapping of keys to primitives, lists, or nested dicts.
            When ``expand_paths`` is ``True`` (default) dotted keys are expanded.

        Raises:
            ToonDecodingError: on malformed TOON text (bad headers, row counts,
                invalid quoting, duplicates, etc.).
            TypeError: if ``text`` is not a string.
        """
        flat: MutableMapping[str, JSONValue] = {}
        for key, value in self._iter_decoded_items(text):
            self._store_decoded_value(flat, key, value)

        collection = dict(flat)
        if self.expand_paths:
            expanded_flat = {
                key: self._expand_nested_value(value)
                for key, value in collection.items()
            }
            return self._expand_dotted_paths(expanded_flat)

        return collection

    # ------------------------------------------------------------------
    # Public streaming API
    # ------------------------------------------------------------------

    def decode_stream(self, text: str) -> Iterator[tuple[str, JSONValue]]:
        """
        Yield TOON key/value pairs as they are parsed.

        Returns dotted keys regardless of ``expand_paths`` to avoid buffering large
        structures. Duplicate keys raise :class:`ToonDecodingError`.
        """
        seen: set[str] = set()

        for key, value in self._iter_decoded_items(text):
            if key in seen:
                raise ToonDecodingError(
                    f"Key '{key}' already exists; duplicate entries are not allowed."
                )
            seen.add(key)
            yield key, value

    # ------------------------------------------------------------------
    # Encoder helpers
    # ------------------------------------------------------------------

    @staticmethod
    def _store_decoded_value(
        flat: MutableMapping[str, JSONValue],
        key: str,
        value: JSONValue,
    ) -> None:
        """
        Store a decoded top-level value, raising on duplicates.
        """
        if key in flat:
            raise ToonDecodingError(
                f"Key '{key}' already exists; duplicate entries are not allowed."
            )

        flat[key] = value

    def _iter_decoded_items(self, text: str) -> Iterator[tuple[str, JSONValue]]:
        if not isinstance(text, str):
            raise TypeError(f"ToonCodec.decode expects a string, got {type(text)}")

        raw_lines = text.splitlines()
        lines: list[str] = [line.rstrip("\n") for line in raw_lines]

        i = 0
        n = len(lines)

        while i < n:
            line = lines[i]

            # Skip empty lines and full-line comments
            if not line.strip() or line.lstrip().startswith("#"):
                i += 1
                continue

            # Tabular array header?
            header_match = self._HEADER_TABLE_RE.match(line)
            if header_match:
                schema = self._parse_header_table(line)

                # Collect table body
                body: list[str] = []
                i += 1
                while i < n:
                    next_line = lines[i]
                    if not next_line.strip():
                        body.append(next_line)
                        i += 1
                        continue
                    if next_line[0].isspace():
                        body.append(next_line)
                        i += 1
                        continue
                    break

                rows = self._parse_table_rows(schema, body)
                yield schema.name, cast(JSONValue, rows)
                continue

            # Primitive array line?
            prim_match = self._HEADER_PRIM_ARRAY_RE.match(line)
            if prim_match:
                key, length_str, raw_values = prim_match.group(
                    "name",
                    "n_items",
                    "values",
                )
                expected_len = int(length_str)
                values = self._parse_primitive_array_values(raw_values)

                if len(values) != expected_len:
                    raise ToonDecodingError(
                        f"Array '{key}' declares length {expected_len}, "
                        f"but {len(values)} values were parsed."
                    )

                yield key, cast(JSONValue, values)
                i += 1
                continue

            # Scalar line
            key, value = self._parse_scalar_line(line)
            yield key, value
            i += 1

    @staticmethod
    def _is_json_primitive(value: Any) -> bool:
        """Return True if value is a JSON primitive type."""
        return isinstance(value, (str, int, float, bool)) or value is None

    def _encode_field(
        self,
        key: str,
        value: Any,
        indent: int,
        *,
        pretty_tables: bool,
    ) -> list[str]:
        """
        Encode a single top-level field (key + value) into one or more lines.
        """
        if not isinstance(key, str):
            raise TypeError(f"Top-level key must be a string, got {type(key)}")

        # Nested objects -> flatten into dotted scalar keys
        if isinstance(value, Mapping):
            flattened = self._flatten_object(prefix=key, obj=value)
            lines = [
                self._format_scalar_line(k, v, indent=indent)
                for k, v in flattened.items()
            ]
            return lines

        # Sequences -> choose array encoding
        if isinstance(value, Sequence) and not isinstance(
            value, (str, bytes, bytearray)
        ):
            return self._encode_array_field(
                key,
                value,
                indent=indent,
                pretty_tables=pretty_tables,
            )

        # Primitive scalar
        if not self._is_json_primitive(value):
            raise TypeError(
                f"Unsupported scalar value for key '{key}': {value!r} "
                f"(type {type(value)})"
            )

        return [self._format_scalar_line(key, value, indent=indent)]

    def _encode_array_field(
        self,
        key: str,
        seq: Sequence[Any],
        indent: int,
        *,
        pretty_tables: bool,
    ) -> list[str]:
        """
        Encode a list value under a given key.

        Strategy:
            * Empty      -> 'key[0]:'
            * All prims  -> primitive array 'key[N]: v1,v2,...'
            * All dicts  -> attempt tabular encoding (with row flattening)
        """
        indent_str = " " * indent

        if len(seq) == 0:
            return [f"{indent_str}{key}[0]:"]

        # All primitives -> inline primitive array
        if all(self._is_json_primitive(item) for item in seq):
            header = f"{indent_str}{key}[{len(seq)}]: "
            values = ",".join(self._format_primitive(v) for v in seq)
            return [header + values]

        # All mappings -> tabular table (rows may contain nested dicts)
        if all(isinstance(item, Mapping) for item in seq):
            rows = [self._flatten_row(row) for row in seq]
            schema = self._infer_schema(name=key, rows=rows)
            indent_for_table = indent + 2 if pretty_tables else indent
            return self._format_table_block(
                schema,
                rows,
                indent=indent_for_table,
            )

        raise ToonEncodingError(
            f"Cannot encode list for key '{key}': "
            "mixed or unsupported element types. "
            "Lists must be all primitives or all (possibly nested) objects."
        )

    # ---- flattening ---------------------------------------------------

    def _flatten_object(
        self,
        prefix: str,
        obj: Mapping[str, Any],
    ) -> dict[str, JSONPrimitive]:
        """
        Flatten a nested object into dotted keys, starting with 'prefix'.

        Example:
            prefix='metadata', obj={'user': {'id': 1}}
            -> {'metadata.user.id': 1}

        Nested arrays inside objects are not supported and will raise.
        """
        flat: dict[str, JSONPrimitive] = {}

        def rec(current_prefix: str, value: Any) -> None:
            if isinstance(value, Mapping):
                # Recursively flatten nested objects by joining keys with dots
                for sub_key, sub_val in value.items():
                    if not isinstance(sub_key, str):
                        raise TypeError(
                            f"Nested object key must be string, got {type(sub_key)}"
                        )
                    # Build dotted path: 'user.id', 'metadata.user.id', etc.
                    new_prefix = (
                        f"{current_prefix}.{sub_key}" if current_prefix else sub_key
                    )
                    rec(new_prefix, sub_val)
            elif self._is_json_primitive(value):
                flat[current_prefix] = value
            elif isinstance(value, Sequence) and not isinstance(
                value, (str, bytes, bytearray)
            ):
                raise ToonEncodingError(
                    "Arrays nested inside objects are not supported "
                    "by this codec. Consider lifting them to top-level "
                    "or encoding that part as JSON."
                )
            else:
                raise TypeError(
                    f"Unsupported value inside object at '{current_prefix}': "
                    f"{value!r} (type {type(value)})"
                )

        rec(prefix, obj)
        return flat

    def _flatten_row(self, row: Mapping[str, Any]) -> dict[str, JSONPrimitive]:
        """
        Flatten a row dict for tabular encoding.

        Nested objects are turned into dotted column names, but arrays
        inside rows are not supported.

        Example row:
            {
                "timestamp": "...",
                "payload": {"sensor": "toilet", "room": "bathroom"}
            }

        -> {
                "timestamp": "...",
                "payload.sensor": "toilet",
                "payload.room": "bathroom"
           }
        """
        flat: dict[str, JSONPrimitive] = {}

        def rec(prefix: str, value: Any) -> None:
            if isinstance(value, Mapping):
                # Flatten nested objects within the row into dotted columns
                for sub_key, sub_val in value.items():
                    if not isinstance(sub_key, str):
                        raise TypeError(f"Row key must be string, got {type(sub_key)}")
                    new_prefix = f"{prefix}.{sub_key}" if prefix else sub_key
                    rec(new_prefix, sub_val)
            elif self._is_json_primitive(value):
                flat[prefix] = value
            elif isinstance(value, Sequence) and not isinstance(
                value, (str, bytes, bytearray)
            ):
                raise ToonEncodingError(
                    "Arrays nested inside tabular rows are not supported by this codec."
                )
            else:
                raise TypeError(
                    f"Unsupported value in row at '{prefix}': "
                    f"{value!r} (type {type(value)})"
                )

        for key, val in row.items():
            rec(key, val)

        if not flat:
            raise ToonEncodingError("Row cannot be flattened into any columns.")

        return flat

    # ---- schema and formatting ----------------------------------------

    def _infer_schema(
        self,
        name: str,
        rows: Sequence[Mapping[str, JSONPrimitive]],
    ) -> ToonTableSchema:
        """
        Infer a table schema from flattened rows.

        All rows must share the same set of keys.

        Raises:
            ToonEncodingError: if later rows differ in their field sets.
        """
        first_keys: list[str] = list(rows[0].keys())
        first_set = set(first_keys)

        for idx, row in enumerate(rows[1:], start=1):
            if set(row.keys()) != first_set:
                raise ToonEncodingError(
                    f"Row {idx} has fields {set(row.keys())!r}, "
                    f"but the first row has {first_set!r}. "
                    "Tabular encoding requires homogeneous field sets."
                )

        return ToonTableSchema(name=name, field_names=first_keys, n_rows=len(rows))

    def _format_table_block(
        self,
        schema: ToonTableSchema,
        rows: Sequence[Mapping[str, JSONPrimitive]],
        indent: int,
    ) -> list[str]:
        """
        Format a complete table block: header + body lines.
        """
        header = self._format_header_line(schema, indent=indent)
        body_lines = [
            self._format_row_line(schema.field_names, row, indent=indent + 2)
            for row in rows
        ]
        return [header, *body_lines]

    @staticmethod
    def _format_header_line(schema: ToonTableSchema, indent: int) -> str:
        """
        Format the header line for a tabular array:

            metrics[5]{date,views,...}:
        """
        indent_str = " " * indent
        fields = ",".join(schema.field_names)
        return f"{indent_str}{schema.name}[{schema.n_rows}]{{{fields}}}:"

    def _format_row_line(
        self,
        field_names: list[str],
        row: Mapping[str, JSONPrimitive],
        indent: int,
    ) -> str:
        """
        Format a single tabular row with indentation.
        """
        indent_str = " " * indent
        values: list[str] = []
        for field in field_names:
            if field not in row:
                raise ToonEncodingError(f"Missing field '{field}' in row {row!r}")
            values.append(self._format_primitive(row[field]))
        return indent_str + ",".join(values)

    def _format_scalar_line(self, key: str, value: Any, indent: int = 0) -> str:
        """
        Format a scalar 'key: value' line with optional indentation.
        """
        indent_str = " " * indent
        if not isinstance(key, str):
            raise TypeError(f"Scalar key must be string, got {type(key)}")
        if not self._is_json_primitive(value):
            raise TypeError(
                f"Scalar value for key '{key}' must be a JSON primitive, "
                f"got {value!r} (type {type(value)})"
            )
        cell = self._format_primitive(value)
        return f"{indent_str}{key}: {cell}"

    @staticmethod
    def _format_primitive(value: JSONPrimitive) -> str:
        """
        Convert a JSON primitive to a TOON cell string.

        Rules:
            * None   -> 'null'
            * bool   -> 'true' / 'false'
            * number -> plain string
            * string -> unquoted if 'simple'; else JSON-quoted.
        """
        if value is None:
            return "null"
        if isinstance(value, bool):
            return "true" if value else "false"
        if isinstance(value, (int, float)):
            return str(value)

        s = str(value)

        # Quote strings that contain CSV delimiters, quotes, or leading/trailing spaces
        # to avoid ambiguity when parsing CSV rows
        needs_quotes = (
            s == "" or "," in s or "\n" in s or "\r" in s or '"' in s or s.strip() != s
        )

        if not needs_quotes:
            return s

        return json.dumps(s, ensure_ascii=False)

    # ------------------------------------------------------------------
    # Decoder helpers
    # ------------------------------------------------------------------

    # Tabular array header: matches lines like "events[3]{time,type,user.id}:"
    # Captures: name (allows dots), n_rows (integer), fields (comma-separated)
    _HEADER_TABLE_RE = re.compile(
        r"""
        ^\s*
        (?P<name>[A-Za-z_][A-Za-z0-9_.]*)
        \[
            (?P<n_rows>\d+)
        \]
        \{
            (?P<fields>[^}]*)
        \}
        :
        \s*$
        """,
        re.VERBOSE,
    )

    # Primitive array header: matches lines like "tags[4]: foo,bar,baz,qux"
    # Captures: name (allows dots), n_items (integer), values (CSV string)
    _HEADER_PRIM_ARRAY_RE = re.compile(
        r"""
        ^\s*
        (?P<name>[A-Za-z_][A-Za-z0-9_.]*)
        \[
            (?P<n_items>\d+)
        \]
        :
        \s*
        (?P<values>.*?)
        \s*$
        """,
        re.VERBOSE,
    )

    # Scalar line: matches "key: value" or "dotted.key: value"
    # Captures: key (identifier or dotted path), value (any text)
    _SCALAR_RE = re.compile(
        r"""
        ^\s*
        (?P<key>[A-Za-z_][A-Za-z0-9_.]*)
        \s*:
        \s*
        (?P<value>.*?)
        \s*$
        """,
        re.VERBOSE,
    )

    def _parse_header_table(self, line: str) -> ToonTableSchema:
        """Parse a tabular array header into a ToonTableSchema."""
        match = self._HEADER_TABLE_RE.match(line)
        if not match:
            raise ToonDecodingError(f"Invalid TOON table header: {line!r}")

        name = match.group("name")
        n_rows = int(match.group("n_rows"))
        fields_raw = match.group("fields").strip()

        if not fields_raw:
            raise ToonDecodingError("Table header must list at least one field.")

        field_names = [f.strip() for f in fields_raw.split(",") if f.strip()]
        if not field_names:
            raise ToonDecodingError("No valid field names found in table header.")

        return ToonTableSchema(name=name, field_names=field_names, n_rows=n_rows)

    def _parse_table_rows(
        self,
        schema: ToonTableSchema,
        body_lines: Iterable[str],
    ) -> list[JSONDict]:
        """
        Parse table body lines according to the schema.

        Blank lines are ignored; each non-blank line is parsed using
        JSON-aware CSV splitting (matching the encoder's formatting).
        """
        rows: list[JSONDict] = []

        for idx, raw_line in enumerate(body_lines):
            if not raw_line.strip():
                continue

            line = raw_line.lstrip()

            cells = self._split_cells(line, context=f"table '{schema.name}' row {idx}")

            if len(cells) != len(schema.field_names):
                raise ToonDecodingError(
                    f"Row {idx} in table '{schema.name}' has {len(cells)} cells; "
                    f"{len(schema.field_names)} expected."
                )

            parsed = [self._parse_cell(cell) for cell in cells]
            rows.append(dict(zip(schema.field_names, parsed, strict=False)))

        if len(rows) != schema.n_rows:
            raise ToonDecodingError(
                f"Header for table '{schema.name}' declares {schema.n_rows} rows, "
                f"but {len(rows)} rows were parsed."
            )

        return rows

    def _parse_primitive_array_values(self, raw_values: str) -> list[JSONPrimitive]:
        """
        Parse the value part of a primitive array line:
            'a,b,c' -> ['a', 'b', 'c']
        """
        if raw_values.strip() == "":
            return []

        cells = self._split_cells(raw_values, context="primitive array")
        return [self._parse_cell(cell) for cell in cells]

    def _parse_scalar_line(self, line: str) -> tuple[str, JSONPrimitive]:
        """
        Parse a 'key: value' scalar line into (key, primitive).
        """
        match = self._SCALAR_RE.match(line)
        if not match:
            raise ToonDecodingError(f"Invalid scalar line: {line!r}")

        key = match.group("key")
        raw_value = match.group("value")

        if raw_value == "":
            return key, None

        return key, self._parse_cell(raw_value)

    def _split_cells(self, raw: str, *, context: str) -> list[str]:
        """
        Split a comma-separated line into cells using the encoder's JSON-style quoting.
        """
        cells: list[str] = []
        current: list[str] = []
        in_quotes = False
        escape = False

        for ch in raw:
            if escape:
                current.append(ch)
                escape = False
                continue

            if ch == "\\" and in_quotes:
                current.append(ch)
                escape = True
                continue

            if ch == '"':
                current.append(ch)
                in_quotes = not in_quotes
                continue

            if ch == "," and not in_quotes:
                cells.append("".join(current))
                current = []
                continue

            current.append(ch)

        if escape:
            raise ToonDecodingError(
                f"Dangling escape sequence while parsing {context}: {raw!r}"
            )
        if in_quotes:
            raise ToonDecodingError(
                f"Unterminated quoted value while parsing {context}: {raw!r}"
            )

        cells.append("".join(current))
        return cells

    @staticmethod
    def _parse_cell(cell: str) -> JSONPrimitive:
        """
        Parse a single TOON cell into a JSON primitive.

        Priority order (important for type inference):
            1. Literal true/false/null
            2. Quoted string (JSON-decoded)
            3. Integer
            4. Float
            5. Fallback to unquoted string
        """
        s = cell.strip()

        # Step 1: Recognize JSON literals
        if s == "true":
            return True
        if s == "false":
            return False
        if s == "null":
            return None

        # Step 2: JSON-quoted strings take precedence over numeric parsing
        if len(s) >= 2 and s[0] == '"' and s[-1] == '"':
            try:
                result: str = json.loads(s)
                return result
            except json.JSONDecodeError as exc:
                raise ToonDecodingError(f"Invalid quoted string cell: {s!r}") from exc

        # Step 3: Try integer parsing (avoid float for exact integers)
        try:
            return int(s)
        except ValueError:
            pass

        # Step 4: Try float parsing
        try:
            return float(s)
        except ValueError:
            pass

        # Step 5: Fallback to unquoted string (e.g., identifiers, dates)
        return s

    # ---- dotted-path expansion ----------------------------------------

    @staticmethod
    def _expand_dotted_paths(
        flat: Mapping[str, JSONValue],
    ) -> JSONDict:
        """
        Expand dotted keys like 'metadata.user.id' into nested dicts.

        Conflicts (same path used for both scalar and container) raise an error.
        """
        root: JSONDict = {}

        for key, value in flat.items():
            parts = key.split(".")
            current: dict[str, Any] = root

            # Navigate/create intermediate nested dicts for all parts except the last
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                elif not isinstance(current[part], dict):
                    # Conflict: 'foo' was already set to a scalar, but we need 'foo.bar'
                    raise ToonDecodingError(
                        f"Path conflict when expanding '{key}': "
                        f"'{part}' is already a non-dict value."
                    )
                current = current[part]  # type: ignore[assignment]

            # Set the final leaf value
            last = parts[-1]
            if last in current:
                raise ToonDecodingError(
                    f"Path conflict when expanding '{key}': '{last}' already exists."
                )
            current[last] = value

        return root

    def _expand_nested_value(self, value: JSONValue) -> JSONValue:
        """
        Recursively expand dotted keys inside nested dicts/lists.

        Used during decode() so that table rows and other nested structures
        regain their original JSON shapes.
        """
        if isinstance(value, list):
            return [self._expand_nested_value(item) for item in value]

        if isinstance(value, dict):
            expanded = self._expand_dotted_paths(value)
            return {
                key: self._expand_nested_value(sub_value)
                for key, sub_value in expanded.items()
            }

        return value
