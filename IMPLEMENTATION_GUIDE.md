# AsyncAPI Discovery - Implementation Guide

## Overview

AsyncAPI Discovery is a tool that automatically scans code repositories to discover event producers and generates AsyncAPI specifications for them. It works with multiple messaging brokers and platforms, providing a unified catalog of all event-driven APIs in your organization.

## Architecture

### Components

1. **main.py** - Entry point and orchestration
   - Parses command-line arguments
   - Loads configuration
   - Coordinates the discovery process
   - Manages the overall workflow

2. **sourcegraph_client.py** - Sourcegraph API integration
   - Connects to Sourcegraph instance
   - Searches code across repositories
   - Retrieves repository lists
   - Fetches file contents

3. **event_detector.py** - Event pattern detection
   - Identifies event producer patterns
   - Supports multiple broker types:
     - Apache Kafka
     - RabbitMQ
     - AWS SNS/SQS
     - Google Pub/Sub
     - Azure Service Bus
     - Generic event emitters
   - Extracts event metadata from code

4. **catalog_manager.py** - AsyncAPI specification generation
   - Creates AsyncAPI 2.6.0 compliant specifications
   - Generates JSON and YAML outputs
   - Maintains catalog index
   - Organizes specifications by repository

5. **demo.py** - Demonstration and testing
   - Shows tool usage with mock data
   - Validates functionality
   - Provides examples

## Installation

### Prerequisites

- Python 3.8 or higher
- Access to a Sourcegraph instance (cloud or self-hosted)
- Sourcegraph API token

### Setup

1. Clone the repository:
```bash
git clone https://github.com/ai-digital-architect/asyncapi_discovery.git
cd asyncapi_discovery
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Configure the tool:
```bash
cp config.json.example config.json
# Edit config.json with your Sourcegraph credentials
```

## Configuration

### config.json Structure

```json
{
  "sourcegraph": {
    "url": "https://sourcegraph.com",
    "token": "your-api-token",
    "timeout": 30
  },
  "event_detection": {
    "brokers": ["kafka", "rabbitmq", "aws", "pubsub", "azure", "generic"],
    "exclude_patterns": ["test", "mock", "example"],
    "include_extensions": [".py", ".java", ".js", ".ts", ".go", ".cs"]
  },
  "output": {
    "directory": "asyncapi_catalog",
    "format": "json",
    "generate_yaml": true
  }
}
```

### Configuration Options

#### Sourcegraph Settings
- `url`: Sourcegraph instance URL
- `token`: API access token (get from Sourcegraph settings)
- `timeout`: Request timeout in seconds

#### Event Detection Settings
- `brokers`: List of broker types to detect
- `exclude_patterns`: Patterns to ignore (e.g., test files)
- `include_extensions`: File extensions to scan

#### Output Settings
- `directory`: Output directory for specifications
- `format`: Output format (json, yaml, or both)
- `generate_yaml`: Generate YAML in addition to JSON

## Usage

### Basic Usage

Scan all repositories and generate AsyncAPI specifications:

```bash
python main.py
```

### Scan Specific Repository

```bash
python main.py --repository github.com/org/repo-name
```

### Custom Configuration

```bash
python main.py --config my-config.json
```

### Custom Output Directory

```bash
python main.py --output /path/to/output
```

### Verbose Logging

```bash
python main.py --verbose
```

### Run Demo

```bash
python demo.py
```

## How It Works

### Discovery Process

1. **Repository Discovery**
   - Connect to Sourcegraph
   - Retrieve list of repositories to scan
   - Filter based on configuration

2. **Code Scanning**
   - Search for event producer patterns
   - Analyze code matches
   - Extract event metadata:
     - Event/topic names
     - Broker types
     - Source file locations
     - Code context

3. **Specification Generation**
   - Create AsyncAPI documents
   - Define channels and messages
   - Generate schemas
   - Add broker configurations

4. **Catalog Creation**
   - Save individual specifications
   - Generate catalog index
   - Create cross-references

### Supported Patterns

#### Kafka
```java
producer.send("topic-name", message);
KafkaProducer<String, String> producer = ...
```

#### RabbitMQ
```python
channel.basic_publish(exchange='events', routing_key='user.created', body=message)
```

#### AWS SNS/SQS
```python
sns.publish(TopicArn='arn:aws:sns:...', Message=message)
sqs.send_message(QueueUrl='https://...', MessageBody=message)
```

#### Google Pub/Sub
```python
publisher.publish(topic_path, data.encode('utf-8'))
```

#### Azure Service Bus
```python
servicebus_client.send_messages(message)
```

#### Generic Events
```javascript
eventEmitter.emit('event-name', data);
publisher.publish('event-name', data);
```

## Output Format

### AsyncAPI Specification

Generated specifications follow AsyncAPI 2.6.0 format:

```json
{
  "asyncapi": "2.6.0",
  "info": {
    "title": "Service Event API",
    "version": "1.0.0",
    "description": "AsyncAPI specification for event producers"
  },
  "servers": {
    "kafka_server": {
      "url": "kafka://localhost",
      "protocol": "kafka"
    }
  },
  "channels": {
    "user.created": {
      "subscribe": {
        "message": {
          "$ref": "#/components/messages/user.created_message"
        }
      }
    }
  },
  "components": {
    "messages": { ... },
    "schemas": { ... }
  }
}
```

### Catalog Index

The tool generates a catalog index file:

```json
{
  "generated_at": "2024-01-01T00:00:00Z",
  "total_specifications": 10,
  "specifications": [
    {
      "repository": "github.com/org/service",
      "title": "Service Event API",
      "version": "1.0.0",
      "channels": 5,
      "file": "github.com_org_service.json"
    }
  ]
}
```

## Extending the Tool

### Add New Broker Support

1. Add patterns to `event_detector.py`:
```python
NEW_BROKER_PATTERNS = [
    r'new_broker_pattern',
    r'another_pattern',
]
```

2. Update pattern compilation in `_compile_patterns()`:
```python
'new_broker': [re.compile(p, re.IGNORECASE) for p in self.NEW_BROKER_PATTERNS]
```

### Custom Event Extraction

Override `_extract_event_name()` in `EventDetector` class to implement custom logic for extracting event names from your codebase.

### Enhanced Schema Generation

Modify `_create_specification()` in `CatalogManager` to generate more detailed schemas based on actual event payloads.

## Troubleshooting

### Common Issues

1. **No repositories found**
   - Check Sourcegraph token permissions
   - Verify Sourcegraph URL is correct
   - Ensure network connectivity

2. **No events detected**
   - Review event detection patterns
   - Check file extensions in configuration
   - Verify exclude patterns aren't too broad

3. **API rate limiting**
   - Increase timeout in configuration
   - Add delays between requests
   - Use self-hosted Sourcegraph instance

### Debug Mode

Enable verbose logging to troubleshoot:

```bash
python main.py --verbose
```

## Best Practices

1. **Start Small**: Test with a single repository first
2. **Review Patterns**: Customize detection patterns for your codebase
3. **Validate Output**: Manually review generated specifications
4. **Iterate**: Refine patterns based on results
5. **Document**: Add context to generated specifications
6. **Version Control**: Track specification changes over time

## Integration

### CI/CD Pipeline

Add to your CI/CD pipeline:

```yaml
- name: Discover AsyncAPI Specifications
  run: |
    python main.py --repository ${{ github.repository }}
    # Upload specifications to artifact repository
```

### Documentation Generation

Use AsyncAPI Generator to create documentation:

```bash
ag asyncapi_catalog/service.json @asyncapi/html-template -o docs/
```

## Future Enhancements

- [ ] Support for additional messaging systems
- [ ] Machine learning for event detection
- [ ] Automatic schema inference from payload examples
- [ ] Integration with API catalogs
- [ ] Real-time monitoring of event flows
- [ ] GraphQL and REST API discovery

## Support

For issues, questions, or contributions:
- GitHub Issues: https://github.com/ai-digital-architect/asyncapi_discovery/issues
- Documentation: https://github.com/ai-digital-architect/asyncapi_discovery

## License

See LICENSE file for details.
