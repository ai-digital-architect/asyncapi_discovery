# AsyncAPI Discovery System

Automated discovery and cataloging of asynchronous events across thousands of applications using SourceGraph and AsyncAPI 3.0.

## Overview

This system automatically:
1. Queries SourceGraph to find event producers across all repositories
2. Detects events from multiple message brokers (Kafka, RabbitMQ, AWS SNS/SQS/EventBridge, IBM MQ)
3. Extracts metadata from source code
4. Generates AsyncAPI 3.0 specifications
5. Creates a comprehensive event catalog

## Supported Technologies

### Message Brokers
- **Apache Kafka** (Spring Kafka, Confluent)
- **RabbitMQ** (Spring AMQP)
- **AWS SNS**
- **AWS SQS**
- **AWS EventBridge**
- **IBM MQ** (JMS)

### Frameworks
- Spring Boot / Spring Cloud Stream
- AWS SDK v2
- Confluent Kafka Client
- IBM MQ JMS

## Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                  AsyncAPI Discovery System                  │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐    ┌─────────────────┐    ┌──────────┐  │
│  │ SourceGraph  │───▶│ Event Detector  │───▶│ AsyncAPI │  │
│  │   Client     │    │    Registry     │    │Generator │  │
│  └──────────────┘    └─────────────────┘    └──────────┘  │
│         │                     │                     │       │
│         │                     │                     ▼       │
│         │                     │            ┌──────────────┐ │
│         │                     └───────────▶│   Catalog    │ │
│         │                                  │   Manager    │ │
│         │                                  └──────────────┘ │
│         │                                          │        │
│         ▼                                          ▼        │
│  ┌──────────────┐                        ┌──────────────┐  │
│  │ Repositories │                        │  AsyncAPI    │  │
│  │  (Bitbucket) │                        │    Specs     │  │
│  └──────────────┘                        └──────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

## Installation

```bash
# Clone or download the project
cd asyncapi_discovery

# Install dependencies
pip install -r requirements.txt
```

## Configuration

Create a `config.json` file:

```json
{
  "sourcegraph": {
    "endpoint": "https://sourcegraph.yourcompany.com",
    "token": "YOUR_TOKEN_HERE"
  },
  "repositories": {
    "include_patterns": ["github.com/yourorg/.*"],
    "exclude_patterns": [".*test.*", ".*demo.*"]
  },
  "output": {
    "directory": "./asyncapi_catalog",
    "format": "yaml"
  },
  "detection": {
    "max_concurrent_queries": 10,
    "timeout_seconds": 300
  }
}
```

### Getting a SourceGraph Token

1. Navigate to your SourceGraph instance
2. Go to User Settings → Access Tokens
3. Create a new token with `read` permissions
4. Copy the token to your config file

## Usage

### Quick Start with Demo

Run the demo with mock data to see how it works:

```bash
python demo.py
```

This will:
- Simulate finding events in your codebase
- Generate AsyncAPI specs
- Create a catalog in `./demo_catalog/`

### Production Use

Run against your actual SourceGraph instance:

```bash
python main.py
```

### Custom Detectors

Add support for additional frameworks:

```python
from event_detector import EventDetector, EventDetectorRegistry

class CustomDetector(EventDetector):
    def get_query(self) -> str:
        return 'lang:python custom.publish patternType:regexp'
    
    def extract_metadata(self, result):
        # Your extraction logic
        return {
            'broker': 'custom-broker',
            'channel_name': 'extracted-channel',
            # ... other fields
        }

# Register it
registry = EventDetectorRegistry()
registry.add_detector('custom-broker', 'custom-framework', CustomDetector())
```

## Output Structure

```
asyncapi_catalog/
├── specs/
│   ├── payment-service.yaml
│   ├── payment-service.json
│   ├── order-service.yaml
│   ├── order-service.json
│   └── ...
├── reports/
│   └── discovery-report-20250128-143022.json
├── catalog-index.json
└── SUMMARY.txt
```

### Generated AsyncAPI Spec Example

```yaml
asyncapi: 3.0.0
info:
  title: Payment Service Event API
  version: 1.0.0
  description: Asynchronous event API for payment-service
servers:
  kafka:
    host: '{environment}.kafka.company.com'
    protocol: kafka
channels:
  payment_processed:
    address: payment.processed
    messages:
      payment_processed_message_0:
        $ref: '#/components/messages/payment_processed_message_0'
operations:
  send_payment_processed:
    action: send
    channel:
      $ref: '#/channels/payment_processed'
components:
  messages:
    payment_processed_message_0:
      name: PaymentEvent
      contentType: application/json
      payload:
        $ref: '#/components/schemas/payment_processed_message_0_payload'
  schemas:
    payment_processed_message_0_payload:
      type: object
      properties:
        eventId:
          type: string
          format: uuid
        timestamp:
          type: string
          format: date-time
```

## Query Examples

The system uses SourceGraph queries like:

```
# Kafka Spring Boot
lang:java (KafkaTemplate.send OR @SendTo) patternType:regexp

# RabbitMQ
lang:java RabbitTemplate.convertAndSend patternType:regexp

# AWS SNS
lang:java AmazonSNS.publish patternType:regexp

# EventBridge
lang:java EventBridgeClient.putEvents patternType:regexp
```

## Extending the System

### Adding New Broker Support

1. Create a new detector class in `event_detector.py`
2. Implement `get_query()` and `extract_metadata()`
3. Register it in `EventDetectorRegistry`

### Schema Enrichment

The generated schemas are templates. To enrich them:

1. Parse actual payload classes from source code
2. Integrate with schema registries (Confluent, AWS Glue)
3. Use static analysis tools to extract field types

### Integration Ideas

- **CI/CD**: Run on every merge to keep catalog updated
- **Schema Registry**: Pull schemas from Confluent/AWS Glue
- **API Gateway**: Auto-configure event routing
- **Documentation**: Generate HTML docs from specs
- **Validation**: Enforce AsyncAPI standards across teams

## SourceGraph Query Tips

### Optimizing Queries

```
# More specific queries return faster
lang:java KafkaTemplate.send file:.*Producer.* 

# Combine patterns
lang:java (pattern1 OR pattern2) repo:^github\.com/yourorg/

# Use regex carefully
patternType:regexp increases query time
```

### Common Patterns

```
# Find all event producers in a specific service
repo:payment-service (KafkaTemplate OR RabbitTemplate)

# Find events by topic name
"user.created" lang:java

# Find all async operations
lang:java (async OR @Async OR CompletableFuture)
```

## Limitations & Future Work

### Current Limitations

1. **Schema Detection**: Currently generates template schemas; doesn't parse actual payload structures
2. **Language Support**: Primarily Java; can be extended to Python, Go, Node.js
3. **Consumer Detection**: Focuses on producers; consumer detection would be valuable
4. **Authentication**: Assumes token-based auth; may need OAuth for enterprise

### Enhancement Ideas

1. **Deep Schema Analysis**
   - Parse Java classes to extract actual schemas
   - Integrate with OpenAPI specs for hybrid APIs
   - Support Avro, Protobuf schema formats

2. **Consumer Mapping**
   - Detect @KafkaListener, @RabbitListener
   - Map producer-consumer relationships
   - Generate sequence diagrams

3. **Runtime Enrichment**
   - Integrate with APM tools (DataDog, New Relic)
   - Capture actual message payloads
   - Monitor schema evolution

4. **Governance**
   - Validate against naming conventions
   - Enforce schema standards
   - Track API lifecycle

## Performance Considerations

- **Concurrent Queries**: Adjust `max_concurrent_queries` based on SourceGraph capacity
- **Result Limits**: Each query can return up to 100 results by default
- **Rate Limiting**: SourceGraph may rate-limit; implement exponential backoff
- **Caching**: Cache SourceGraph results for faster re-runs

## Troubleshooting

### SourceGraph Connection Issues

```
Error: Failed to connect to SourceGraph
Solution: Check endpoint URL and token in config.json
```

### No Events Discovered

```
Possible causes:
1. Queries are too specific
2. Code patterns don't match detectors
3. Repositories are excluded by patterns
```

### Invalid AsyncAPI Specs

```
Use validators:
- https://www.asyncapi.com/tools/validate
- asyncapi-validator CLI tool
```

## Contributing

To add support for new brokers/frameworks:

1. Study the existing detectors in `event_detector.py`
2. Create appropriate SourceGraph queries
3. Implement extraction logic
4. Test with real code samples
5. Document the patterns detected

## License

[Your License Here]

## Resources

- [AsyncAPI Specification](https://www.asyncapi.com/docs/reference/specification/v3.0.0)
- [SourceGraph Query Syntax](https://docs.sourcegraph.com/code_search/reference/queries)
- [Message Broker Documentation](https://www.asyncapi.com/docs/tutorials)

## Contact

For questions or support: [your-email@company.com]