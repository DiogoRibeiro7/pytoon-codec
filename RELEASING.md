# Release Process for pytoon-codec

This document describes the step-by-step process for releasing a new version of `pytoon-codec` to ensure that all version references stay in sync across the codebase, PyPI, and Zenodo.

---

## Pre-Release Checklist

Before creating a new release, ensure:

1. All planned features and bug fixes are merged to the `develop` branch
2. All tests are passing
3. Documentation is up to date
4. No known critical issues

---

## Release Steps

### 1. Update Version Numbers

Update the version in the following files (replace `X.Y.Z` with the new version number):

**`pyproject.toml`:**
```toml
[tool.poetry]
version = "X.Y.Z"
```

**`CITATION.cff`:**
```yaml
version: "X.Y.Z"
```

**Note:** In `CITATION.cff`, the version should NOT have a `v` prefix (e.g., `0.2.0` not `v0.2.0`).

### 2. Update CHANGELOG.md

Add a new section at the top of `CHANGELOG.md` with:

- Release version and date
- Brief summary of changes
- Organized by categories: Added, Changed, Fixed, Removed

Example:
```markdown
## [0.2.0] - 2025-01-20

### Added
- New feature X for handling edge case Y
- Support for configuration option Z

### Changed
- Improved performance of table encoding by 15%

### Fixed
- Bug in nested path expansion with null values
```

### 3. Run Quality Checks

Ensure all quality checks pass before building:

```bash
# Lint check
poetry run ruff check .

# Type check
poetry run mypy src

# Run full test suite
poetry run pytest
```

If any checks fail, fix the issues and repeat until all pass.

### 4. Build the Distribution

Build the package:

```bash
poetry build
```

This creates distribution files in the `dist/` directory:
- `pytoon_codec-X.Y.Z-py3-none-any.whl`
- `pytoon_codec-X.Y.Z.tar.gz`

Verify the build artifacts:
```bash
ls -lh dist/
```

### 5. Commit and Tag

Commit all version updates:

```bash
git add pyproject.toml CITATION.cff CHANGELOG.md
git commit -m "Release version X.Y.Z"
```

Create a Git tag:

```bash
git tag vX.Y.Z
```

**Note:** Git tags should have a `v` prefix (e.g., `v0.2.0`), unlike the version in `CITATION.cff`.

### 6. Push to GitHub

Push the commit and tag to GitHub:

```bash
git push origin develop
git push origin vX.Y.Z
```

This will trigger:
- GitHub Actions CI to run tests
- Zenodo to archive the release (if configured)

### 7. Publish to PyPI (Optional)

When ready to publish to PyPI:

```bash
poetry publish
```

You'll be prompted for PyPI credentials (or use a token configured in Poetry).

**Note:** Publishing to PyPI is permanent and cannot be undone. Double-check the version and build artifacts before publishing.

### 8. Create GitHub Release

1. Go to https://github.com/DiogoRibeiro7/pytoon-codec/releases
2. Click "Draft a new release"
3. Select the tag `vX.Y.Z`
4. Set release title: `pytoon-codec vX.Y.Z`
5. Copy the relevant section from `CHANGELOG.md` into the release description
6. Attach the build artifacts from `dist/` (optional)
7. Click "Publish release"

### 9. Verify Zenodo Archiving

After creating the GitHub release:

1. Check that Zenodo has picked up the new release at https://zenodo.org/
2. Verify the Zenodo record has the correct:
   - Version number
   - DOI
   - Metadata (from `.zenodo.json`)
3. Update `README.md` with the new Zenodo DOI badge (replace `XXXXXXX` with actual DOI)

---

## Post-Release

After publishing:

1. Announce the release (if applicable):
   - GitHub Discussions
   - Project website
   - Social media
2. Monitor for any immediate issues
3. Bump to next development version if using semantic versioning with `-dev` suffix

---

## Version Numbering

This project follows [Semantic Versioning](https://semver.org/) (SemVer):

- **MAJOR** version (X.0.0): Incompatible API changes
- **MINOR** version (0.X.0): New functionality, backwards-compatible
- **PATCH** version (0.0.X): Backwards-compatible bug fixes

Examples:
- `0.1.0` → `0.1.1`: Bug fix release
- `0.1.1` → `0.2.0`: New feature added
- `0.2.0` → `1.0.0`: Breaking API change

---

## Quick Reference

```bash
# Full release workflow
# 1. Update versions in pyproject.toml and CITATION.cff
# 2. Update CHANGELOG.md
# 3. Run checks
poetry run ruff check .
poetry run mypy src
poetry run pytest

# 4. Build
poetry build

# 5. Commit and tag
git add pyproject.toml CITATION.cff CHANGELOG.md
git commit -m "Release version X.Y.Z"
git tag vX.Y.Z

# 6. Push
git push origin develop
git push origin vX.Y.Z

# 7. Publish (when ready)
poetry publish

# 8. Create GitHub release and verify Zenodo
```

---

## Troubleshooting

### Tests fail during pre-release checks

- Fix the failing tests before proceeding
- Do not release with known test failures

### Poetry build fails

- Check `pyproject.toml` syntax
- Ensure all dependencies are properly specified
- Run `poetry check` to validate configuration

### Git tag already exists

- If you need to re-tag: `git tag -d vX.Y.Z` (local), `git push origin :refs/tags/vX.Y.Z` (remote)
- Use a new patch version instead

### PyPI publish fails

- Verify PyPI credentials: `poetry config pypi-token.pypi <your-token>`
- Check that version doesn't already exist on PyPI (versions are immutable)
- Ensure package name is available

### Zenodo not picking up release

- Check GitHub-Zenodo integration settings
- Ensure `.zenodo.json` is valid JSON
- Tag must be pushed before creating GitHub release
- May take a few minutes for Zenodo to process

---

## Contact

For questions about the release process, open an issue on GitHub.
