# AsyncAPI Discovery

[![CI](https://github.com/ai-digital-architect/asyncapi_discovery/workflows/CI/badge.svg)](https://github.com/ai-digital-architect/asyncapi_discovery/actions)
[![codecov](https://codecov.io/gh/ai-digital-architect/asyncapi_discovery/branch/main/graph/badge.svg)](https://codecov.io/gh/ai-digital-architect/asyncapi_discovery)
[![PyPI version](https://badge.fury.io/py/asyncapi-discovery.svg)](https://badge.fury.io/py/asyncapi-discovery)
[![Python Versions](https://img.shields.io/pypi/pyversions/asyncapi-discovery.svg)](https://pypi.org/project/asyncapi-discovery/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

Scan repositories for event producers regardless of the broker and create AsyncAPI catalog specifications for those.

## Features

- 🔍 **Automatic Discovery**: Scans repositories to find event producers in multiple languages
- 📋 **AsyncAPI Generation**: Creates AsyncAPI 2.6.0 specifications automatically
- 🚀 **Broker Agnostic**: Works with any message broker (Kafka, RabbitMQ, AMQP, etc.)
- 🐍 **Multi-Language Support**: Supports Python, JavaScript, TypeScript, Java, and Go
- 🛠️ **CLI Tool**: Easy-to-use command-line interface
- 📦 **Python API**: Programmatic access for integration into your tools

## Installation

### From PyPI (coming soon)

```bash
pip install asyncapi-discovery
```

### From Source

```bash
git clone https://github.com/ai-digital-architect/asyncapi_discovery.git
cd asyncapi_discovery
pip install -e .
```

## Quick Start

### Command Line Usage

Scan a repository and generate an AsyncAPI specification:

```bash
asyncapi-discovery /path/to/your/repository -o asyncapi.yaml
```

Discover producers without generating a specification:

```bash
asyncapi-discovery /path/to/your/repository --discover-only
```

Enable verbose output:

```bash
asyncapi-discovery /path/to/your/repository -v -o asyncapi.yaml
```

### Python API Usage

```python
from asyncapi_discovery import AsyncAPIDiscovery

# Initialize discovery for a repository
discovery = AsyncAPIDiscovery('/path/to/your/repository')

# Discover event producers
producers = discovery.discover()
print(f"Found {producers['statistics']['producers_found']} producers")

# Generate AsyncAPI specification
spec = discovery.generate_spec(producers)
print(spec)

# Or run the complete workflow
spec = discovery.run('asyncapi.yaml')
```

## How It Works

AsyncAPI Discovery scans your repository for common event producer patterns in your code:

1. **Scanning**: Analyzes source files for event publishing patterns
2. **Detection**: Identifies calls to `publish()`, `send()`, `emit()`, `produce()` and similar methods
3. **Extraction**: Extracts event names and metadata
4. **Generation**: Creates a standardized AsyncAPI specification

## Supported Languages and Patterns

- **Python**: `publish()`, `send()`, `emit()`, `produce()`
- **JavaScript/TypeScript**: `publish()`, `send()`, `emit()`, `produce()`
- **Java**: `publish()`, `send()`, `produce()`
- **Go**: `Publish()`, `Send()`, `Produce()`

## Development

### Setup Development Environment

```bash
# Clone the repository
git clone https://github.com/ai-digital-architect/asyncapi_discovery.git
cd asyncapi_discovery

# Create virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install development dependencies
pip install -e ".[dev]"

# Install pre-commit hooks
pre-commit install
```

### Running Tests

```bash
# Run all tests
pytest

# Run with coverage
pytest --cov=asyncapi_discovery --cov-report=html

# Run specific test file
pytest tests/test_scanner.py
```

### Code Quality

```bash
# Lint with ruff
ruff check src/ tests/

# Format with black
black src/ tests/

# Type check with mypy
mypy src/
```

## Contributing

Contributions are welcome! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

- [ ] Support for more message brokers (SQS, Google Pub/Sub, Azure Service Bus)
- [ ] Enhanced pattern detection for framework-specific patterns
- [ ] Support for AsyncAPI 3.0
- [ ] Integration with CI/CD pipelines
- [ ] Web UI for visualization
- [ ] Support for consumer detection

## Links

- [Documentation](https://github.com/ai-digital-architect/asyncapi_discovery)
- [Issue Tracker](https://github.com/ai-digital-architect/asyncapi_discovery/issues)
- [PyPI Package](https://pypi.org/project/asyncapi-discovery/)
- [AsyncAPI Specification](https://www.asyncapi.com/docs/reference/specification/v2.6.0)
