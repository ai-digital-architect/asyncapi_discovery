# AsyncAPI Discovery

> Automatically discover event producers in your codebase and generate AsyncAPI specifications

## Overview

AsyncAPI Discovery is a powerful tool that scans code repositories to identify event producers across various messaging systems and brokers, automatically generating AsyncAPI catalog specifications. It helps document your event-driven architecture regardless of the messaging technology used.

## Features

- 🔍 **Multi-Broker Support**: Detects event producers across:
  - Apache Kafka
  - RabbitMQ
  - AWS SNS/SQS
  - Google Pub/Sub
  - Azure Service Bus
  - Generic event emitters

- 📊 **AsyncAPI Generation**: Creates AsyncAPI 2.6.0 compliant specifications
- 🔌 **Sourcegraph Integration**: Leverages Sourcegraph for powerful code search
- 📚 **Catalog Management**: Organizes specifications in a searchable catalog
- 🎯 **Pattern Recognition**: Uses regex patterns to identify event patterns
- 🌐 **Multi-Language**: Supports Python, Java, JavaScript, TypeScript, Go, C#

## Quick Start

### Prerequisites

- Python 3.8+
- Sourcegraph instance access (cloud or self-hosted)
- Sourcegraph API token

### Installation

```bash
# Clone the repository
git clone https://github.com/ai-digital-architect/asyncapi_discovery.git
cd asyncapi_discovery

# Install dependencies (when available)
pip install -r requirements.txt

# Configure your Sourcegraph credentials
cp config.json config.local.json
# Edit config.local.json with your credentials
```

### Usage

```bash
# Scan all repositories
python main.py

# Scan a specific repository
python main.py --repository github.com/org/repo-name

# Use custom configuration
python main.py --config config.local.json

# Run demo
python demo.py
```

## Configuration

Create a `config.json` file with your settings:

```json
{
  "sourcegraph": {
    "url": "https://sourcegraph.com",
    "token": "your-api-token",
    "timeout": 30
  },
  "event_detection": {
    "brokers": ["kafka", "rabbitmq", "aws", "pubsub", "azure", "generic"],
    "exclude_patterns": ["test", "mock"],
    "include_extensions": [".py", ".java", ".js", ".ts", ".go", ".cs"]
  },
  "output": {
    "directory": "asyncapi_catalog",
    "format": "json",
    "generate_yaml": true
  }
}
```

## Project Structure

```
asyncapi_discovery/
├── .github/              # GitHub configuration
│   ├── prompts/         # AI prompts
│   ├── chatmodes/       # Chat mode configurations
│   ├── instructions/    # Instructions and guides
│   └── workflows/       # GitHub Actions workflows
├── .specify/            # Specify configuration
├── main.py              # Main entry point
├── sourcegraph_client.py # Sourcegraph API client
├── event_detector.py    # Event detection logic
├── catalog_manager.py   # AsyncAPI catalog management
├── demo.py              # Demonstration script
├── config.json          # Configuration file
├── README.md            # This file
└── IMPLEMENTATION_GUIDE.md # Detailed implementation guide
```

## How It Works

1. **Connect**: Connects to your Sourcegraph instance
2. **Scan**: Searches for event producer patterns in code
3. **Extract**: Identifies event names, brokers, and metadata
4. **Generate**: Creates AsyncAPI specifications
5. **Catalog**: Organizes specifications in a catalog

## Output

The tool generates:

- Individual AsyncAPI specifications (JSON/YAML) for each repository
- A catalog index with metadata about all specifications
- Organized directory structure for easy navigation

Example output:
```
asyncapi_catalog/
├── catalog_index.json
├── github.com_org_service1.json
├── github.com_org_service1.yaml
├── github.com_org_service2.json
└── github.com_org_service2.yaml
```

## Documentation

For detailed implementation information, see [IMPLEMENTATION_GUIDE.md](IMPLEMENTATION_GUIDE.md)

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

See LICENSE file for details.

## Support

For questions or issues:
- Open an issue on GitHub
- Check the [Implementation Guide](IMPLEMENTATION_GUIDE.md)

## Acknowledgments

Built with ❤️ using:
- [AsyncAPI](https://www.asyncapi.com/) specification
- [Sourcegraph](https://sourcegraph.com/) code search
