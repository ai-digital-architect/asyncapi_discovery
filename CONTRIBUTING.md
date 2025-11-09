# Contributing to AsyncAPI Discovery

Thank you for your interest in contributing to AsyncAPI Discovery! This document provides guidelines and instructions for contributing.

## Development Setup

1. Clone the repository:
   ```bash
   git clone https://github.com/ai-digital-architect/asyncapi_discovery.git
   cd asyncapi_discovery
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. Install development dependencies:
   ```bash
   pip install -e ".[dev]"
   ```

4. Install pre-commit hooks:
   ```bash
   pip install pre-commit
   pre-commit install
   ```

## Running Tests

Run all tests:
```bash
pytest
```

Run tests with coverage:
```bash
pytest --cov=asyncapi_discovery --cov-report=html
```

## Code Quality

### Linting
```bash
ruff check src/ tests/
```

### Formatting
```bash
black src/ tests/
```

### Type Checking
```bash
mypy src/
```

## Making Changes

1. Create a new branch for your feature or bugfix:
   ```bash
   git checkout -b feature/your-feature-name
   ```

2. Make your changes and ensure all tests pass.

3. Add tests for new functionality.

4. Commit your changes with a descriptive commit message:
   ```bash
   git commit -m "Add feature: description"
   ```

5. Push to your fork and submit a pull request.

## Pull Request Guidelines

- Keep pull requests focused on a single feature or fix
- Include tests for new functionality
- Update documentation as needed
- Ensure all tests pass and code quality checks succeed
- Write clear commit messages and PR descriptions

## Code Style

- Follow PEP 8 guidelines
- Use type hints where appropriate
- Write docstrings for all public functions and classes
- Keep line length to 100 characters (enforced by black)

## Reporting Issues

When reporting issues, please include:
- A clear description of the problem
- Steps to reproduce the issue
- Expected behavior
- Actual behavior
- Your environment (OS, Python version, etc.)

## Questions?

Feel free to open an issue for any questions about contributing.
