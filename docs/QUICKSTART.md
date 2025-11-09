# Quick Start Guide

Get started with AsyncAPI Discovery in 5 minutes!

## Installation

```bash
# From source (for now)
git clone https://github.com/ai-digital-architect/asyncapi_discovery.git
cd asyncapi_discovery
pip install -e .
```

## Basic Usage

### 1. Scan Your Repository

```bash
asyncapi-discovery /path/to/your/repository -o asyncapi.yaml
```

This will:
- Scan all source files in your repository
- Detect event producer patterns
- Generate an AsyncAPI 2.6.0 specification
- Save it to `asyncapi.yaml`

### 2. Use Verbose Mode

```bash
asyncapi-discovery /path/to/your/repository -v -o asyncapi.yaml
```

This shows detailed output including:
- Number of files scanned
- Events discovered
- The generated specification

### 3. Discovery Only (No Generation)

```bash
asyncapi-discovery /path/to/your/repository --discover-only
```

This only discovers and lists event producers without generating a specification.

## Python API Usage

### Basic Example

```python
from asyncapi_discovery import AsyncAPIDiscovery

# Initialize
discovery = AsyncAPIDiscovery('/path/to/repository')

# Run discovery and generation
spec = discovery.run('asyncapi.yaml')

print(f"Specification saved to asyncapi.yaml")
```

### Step-by-Step Example

```python
from asyncapi_discovery import AsyncAPIDiscovery

# 1. Initialize
discovery = AsyncAPIDiscovery('/path/to/repository')

# 2. Discover producers
producers = discovery.discover()
print(f"Found {producers['statistics']['producers_found']} producers")

# 3. Generate specification
spec = discovery.generate_spec(producers)

# 4. Save or use the specification
with open('asyncapi.yaml', 'w') as f:
    f.write(spec)
```

## What Gets Detected?

AsyncAPI Discovery looks for common event publishing patterns in your code:

### Python
```python
publish("user.created", user_data)
send("order.placed", order)
emit("notification.sent", notification)
produce("analytics.event", analytics)
```

### JavaScript/TypeScript
```javascript
publish('user.created', userData);
send('order.placed', order);
emit('notification.sent', notification);
produce('analytics.event', analytics);
```

### Java
```java
publish("user.created", userData);
send("order.placed", order);
produce("analytics.event", analytics);
```

### Go
```go
Publish("user.created", userData)
Send("order.placed", order)
Produce("analytics.event", analytics)
```

## Understanding the Output

The generated AsyncAPI specification includes:

1. **Info Section**: Metadata about the specification
2. **Servers**: Default server configuration (can be customized)
3. **Channels**: One channel per discovered event with:
   - Event description
   - Message schema
   - Payload structure

### Example Output

```yaml
asyncapi: 2.6.0
info:
  title: Discovered AsyncAPI Specification
  version: 1.0.0
  description: Auto-generated AsyncAPI specification from repository scanning
servers:
  development:
    url: localhost
    protocol: amqp
    description: Development server
channels:
  user.created:
    description: Channel for user.created event
    subscribe:
      summary: Subscribe to user.created events
      message:
        name: user.created
        title: user.created
        contentType: application/json
        payload:
          type: object
          properties:
            eventId:
              type: string
              description: Unique event identifier
            timestamp:
              type: string
              format: date-time
              description: Event timestamp
            data:
              type: object
              description: Event payload data
```

## Next Steps

- Check out the [examples](../examples/) directory for more usage examples
- Read the full [README](../README.md) for advanced features
- See [CONTRIBUTING.md](../CONTRIBUTING.md) to contribute to the project

## Troubleshooting

### No events detected
- Make sure your code uses one of the supported patterns
- Check that test files are properly excluded (they should be in `/test/` or `/tests/` directories)
- Enable verbose mode (`-v`) to see what files are being scanned

### Wrong events detected
- The tool uses pattern matching, so it may detect false positives
- Review the generated specification and manually edit as needed
- Consider opening an issue with your use case to improve detection

## Getting Help

- [GitHub Issues](https://github.com/ai-digital-architect/asyncapi_discovery/issues)
- [Documentation](https://github.com/ai-digital-architect/asyncapi_discovery)
