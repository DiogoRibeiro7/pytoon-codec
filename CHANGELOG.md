# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [0.1.0] - 2025-01-15

### Added

- Initial implementation of `ToonCodec` encoder/decoder
- Support for time-series data encoding with tabular TOON blocks
- Support for nested events with dotted-path flattening (e.g., `user.id`, `payload.sensor`)
- Round-trip JSON ↔ TOON conversion with type preservation
- Optional dotted-path expansion control via `expand_paths` parameter
- Comprehensive unit tests for:
  - Scalar and primitive value encoding/decoding
  - Primitive arrays
  - Tabular structures (arrays of objects)
  - Nested objects and dotted paths
- Integration tests with realistic payloads:
  - Analytics dashboards
  - IoT sensor events
  - Monitoring alerts
  - LLM conversation context
- Regression tests for:
  - String formatting and quoting edge cases
  - Whitespace and blank line handling
- GitHub Actions CI/CD pipeline:
  - Matrix testing across Python 3.10, 3.11, 3.12
  - Automated linting (ruff)
  - Type checking (mypy)
- Pre-commit hooks for code quality
- Comprehensive documentation:
  - README with usage examples
  - API reference in `docs/api.md`
  - Contributing guidelines
- Citation metadata:
  - `CITATION.cff` for academic citation
  - `.zenodo.json` for Zenodo archiving
- Type hints with full mypy compliance

### Design Constraints

- Top-level must be a mapping (dict-like object)
- Arrays of objects must be homogeneous (consistent field sets)
- No nested arrays in objects
- No mixed-type arrays
- No arrays of arrays

---

## Template for Future Releases

```markdown
## [X.Y.Z] - YYYY-MM-DD

### Added
- New features

### Changed
- Changes to existing functionality

### Deprecated
- Soon-to-be removed features

### Removed
- Removed features

### Fixed
- Bug fixes

### Security
- Security updates
```
