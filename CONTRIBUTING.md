# Contributing to pytoon-codec

Thank you for your interest in contributing to `pytoon-codec`! This document provides guidelines and instructions for contributing to the project.

## Development Setup

### Prerequisites

- Python 3.10 or higher
- [Poetry](https://python-poetry.org/) for dependency management

### Setting Up Your Development Environment

1. **Clone the repository:**

   ```bash
   git clone https://github.com/DiogoRibeiro7/pytoon-codec.git
   cd pytoon-codec
   ```

2. **Install dependencies:**

   ```bash
   poetry install
   ```

   This will create a virtual environment and install all dependencies, including development tools.

3. **Activate the virtual environment:**

   ```bash
   poetry shell
   ```

   Or run commands using `poetry run`:

   ```bash
   poetry run pytest
   ```

## Code Quality Tools

We use several tools to maintain code quality:

- **[Ruff](https://docs.astral.sh/ruff/)**: Fast Python linter and formatter
- **[Mypy](https://mypy.readthedocs.io/)**: Static type checker
- **[Pytest](https://docs.pytest.org/)**: Testing framework
- **[Pre-commit](https://pre-commit.com/)**: Git hook framework

### Running Code Quality Checks

Before submitting a pull request, ensure your code passes all checks:

```bash
# Run linter
poetry run ruff check .

# Run formatter
poetry run ruff format .

# Run type checker
poetry run mypy src

# Run tests
poetry run pytest

# Run all tests with markers
poetry run pytest -m unit      # Unit tests only
poetry run pytest -m integration  # Integration tests only
poetry run pytest -m regression   # Regression tests only
```

### Pre-commit Hooks

We strongly recommend using pre-commit hooks to automatically check your code before each commit.

**Install pre-commit hooks:**

```bash
poetry run pre-commit install
```

**Run pre-commit hooks manually:**

```bash
# Run on all files
poetry run pre-commit run --all-files

# Run on staged files only
poetry run pre-commit run
```

The hooks will:
- Check and fix trailing whitespace
- Ensure files end with a newline
- Check YAML and TOML syntax
- Run Ruff linter and formatter
- Run Mypy type checker on `src/` files

## Testing

### Running Tests

```bash
# Run all tests
poetry run pytest

# Run with verbose output
poetry run pytest -v

# Run specific test file
poetry run pytest tests/test_scalars_and_primitives.py

# Run tests matching a pattern
poetry run pytest -k "test_encode"

# Run with coverage report
poetry run pytest --cov=pytoon_codec --cov-report=html
```

### Test Categories

Tests are organized with pytest markers:

- `@pytest.mark.unit`: Fast, isolated unit tests
- `@pytest.mark.integration`: Integration tests with realistic payloads
- `@pytest.mark.regression`: Tests for previously fixed bugs

### Writing Tests

- Place new tests in the appropriate `tests/test_*.py` file
- Use descriptive test names: `test_<what>_<expected_behavior>`
- Add docstrings explaining what the test validates
- Mark tests with appropriate pytest markers

## Code Style

### Python Style Guidelines

- Follow [PEP 8](https://pep8.org/) style guide (enforced by Ruff)
- Use type hints for all function signatures
- Maximum line length: 88 characters
- Use descriptive variable names
- Add docstrings to all public classes and functions (Google or NumPy style)

### Type Hints

All code in `src/pytoon_codec/` must have type hints:

```python
def encode_value(value: str, max_length: int = 100) -> str:
    """Encode a string value with optional length limit."""
    return value[:max_length]
```

## Pull Request Process

1. **Create a feature branch:**

   ```bash
   git checkout -b feature/your-feature-name
   ```

2. **Make your changes and commit:**

   ```bash
   git add .
   git commit -m "Add feature: description"
   ```

3. **Ensure all checks pass:**

   ```bash
   poetry run pre-commit run --all-files
   poetry run pytest
   ```

4. **Push your branch:**

   ```bash
   git push origin feature/your-feature-name
   ```

5. **Open a Pull Request:**

   - Provide a clear description of your changes
   - Reference any related issues
   - Ensure CI passes

## Continuous Integration

All pull requests must pass CI checks:

-  Linting (Ruff)
-  Formatting (Ruff)
-  Type checking (Mypy)
-  Tests (Pytest on Python 3.10, 3.11, 3.12)

CI runs automatically on all pull requests and pushes to `main` or `develop` branches.

## Reporting Issues

When reporting issues, please include:

- Python version
- Operating system
- Steps to reproduce
- Expected vs. actual behavior
- Relevant code snippets or error messages

## Questions?

Feel free to open an issue for questions or discussions about contributing!

## License

By contributing to `pytoon-codec`, you agree that your contributions will be licensed under the MIT License.
