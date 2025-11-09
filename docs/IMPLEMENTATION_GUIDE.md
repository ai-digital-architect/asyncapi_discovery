# Enterprise Implementation Guide

## Executive Summary

This guide provides a comprehensive roadmap for implementing the AsyncAPI Discovery System across a large enterprise with 1000s of applications using diverse messaging technologies (Kafka, RabbitMQ, AWS services, IBM MQ).

## Prerequisites

### Infrastructure Requirements
- **SourceGraph**: Enterprise deployment with API access
- **Compute**: Python 3.9+ environment with 4GB+ RAM
- **Storage**: 10GB+ for catalog storage
- **Network**: Access to Bitbucket repositories via SourceGraph

### Access Requirements
- SourceGraph API token with read access
- Bitbucket repository access (via SourceGraph)
- CI/CD pipeline access (GitHub Actions, Jenkins, or GitLab CI)

## Implementation Phases

### Phase 1: Proof of Concept (Week 1-2)

**Objectives:**
- Validate the approach with a subset of applications
- Identify any organization-specific patterns
- Establish baseline metrics

**Steps:**
1. Deploy to development environment
2. Configure for 5-10 representative services
3. Run discovery and review results
4. Gather feedback from development teams

**Success Criteria:**
- 80%+ accuracy in event detection
- Generated specs validate against AsyncAPI 3.0
- Execution time < 10 minutes for subset

### Phase 2: Pattern Enhancement (Week 3-4)

**Objectives:**
- Add detectors for organization-specific patterns
- Enhance schema extraction
- Integrate with existing schema registries

**Custom Detector Development:**

```python
# Example: Custom internal framework
class InternalMessageBusDetector(EventDetector):
    def get_query(self) -> str:
        # Your organization's specific patterns
        return 'lang:java InternalMessageBus.publish patternType:regexp'
    
    def extract_metadata(self, result):
        # Custom extraction logic
        snippet = result.get('code_snippet', '')
        
        # Extract your specific patterns
        topic_match = re.search(
            r'publish\s*\(\s*MessageType\.(\w+)',
            snippet
        )
        
        if not topic_match:
            return None
        
        return {
            'broker': 'internal-message-bus',
            'framework': 'internal-framework',
            'service_name': self._extract_service_name(result),
            'channel_name': topic_match.group(1),
            # ... additional fields
        }
```

**Schema Registry Integration:**

```python
# Integrate with Confluent Schema Registry
from confluent_kafka.schema_registry import SchemaRegistryClient

class SchemaRegistryEnricher:
    def __init__(self, registry_url: str):
        self.client = SchemaRegistryClient({'url': registry_url})
    
    async def enrich_from_registry(self, event_metadata):
        topic = event_metadata.get('channel_name')
        
        try:
            # Get latest schema
            schema = self.client.get_latest_version(f"{topic}-value")
            
            # Convert Avro/Protobuf to JSON Schema
            return self._convert_to_json_schema(schema)
        except Exception as e:
            logger.warning(f"Schema not found in registry: {topic}")
            return None
```

### Phase 3: Scaled Rollout (Week 5-8)

**Objectives:**
- Process all repositories
- Establish automated catalog updates
- Deploy catalog portal

**Scaling Considerations:**

1. **Query Optimization**
   ```python
   # Batch queries by language/tech stack
   java_queries = [q for q in queries if 'lang:java' in q['query']]
   python_queries = [q for q in queries if 'lang:python' in q['query']]
   
   # Process in parallel with rate limiting
   ```

2. **Incremental Discovery**
   ```python
   # Only process repositories changed since last run
   last_run = load_last_run_timestamp()
   query = f"repo:yourorg/* modified:after({last_run})"
   ```

3. **Distributed Processing**
   ```bash
   # Split by repository groups
   python main.py --repo-pattern "team-A/*"
   python main.py --repo-pattern "team-B/*"
   ```

### Phase 4: Operationalization (Week 9-12)

**Objectives:**
- Integrate with development workflows
- Establish governance processes
- Enable self-service capabilities

## Architecture Deployment Options

### Option A: Centralized Service

```
┌─────────────────────────────────────────────────────┐
│           AsyncAPI Catalog Service                  │
├─────────────────────────────────────────────────────┤
│                                                     │
│  API Endpoints:                                     │
│  - GET  /api/specs                                  │
│  - GET  /api/specs/{service}                        │
│  - GET  /api/search?query=...                       │
│  - POST /api/trigger-discovery                      │
│                                                     │
│  Scheduler: Daily discovery runs                    │
│  Storage: S3/GCS for catalog                        │
│  Database: Metadata & search index                  │
│                                                     │
└─────────────────────────────────────────────────────┘
```

**Tech Stack:**
- FastAPI or Flask for REST API
- PostgreSQL for metadata
- ElasticSearch for full-text search
- Redis for caching
- S3/GCS for spec storage

### Option B: Static Site Generation

```
┌─────────────────────────────────────────────────────┐
│        CI/CD Pipeline (GitHub Actions)              │
│  1. Run discovery                                   │
│  2. Generate static HTML                            │
│  3. Deploy to GitHub Pages / S3                     │
└─────────────────────────────────────────────────────┘
                         │
                         ▼
┌─────────────────────────────────────────────────────┐
│    Static Catalog Site (https://catalog.company)   │
│  - Searchable interface                             │
│  - Download specs                                   │
│  - View visualizations                              │
└─────────────────────────────────────────────────────┘
```

**Benefits:**
- No server maintenance
- High availability
- Simple deployment

### Option C: Hybrid Approach (Recommended)

Combine both: Static site for consumption, API service for discovery and advanced queries.

## Integration Points

### 1. Schema Registries

**Confluent Schema Registry:**
```python
async def integrate_confluent_registry():
    registry = SchemaRegistryClient({'url': REGISTRY_URL})
    
    for event in events:
        if event['broker'] == 'kafka':
            topic = event['channel_name']
            try:
                schema = registry.get_latest_version(f"{topic}-value")
                event['enriched_schema'] = convert_avro_to_json_schema(schema)
            except SchemaRegistryError:
                pass  # Use extracted schema
```

**AWS Glue Schema Registry:**
```python
import boto3

glue = boto3.client('glue')

def get_schema_from_glue(registry_name, schema_name):
    response = glue.get_schema_version(
        SchemaId={'RegistryName': registry_name, 'SchemaName': schema_name},
        SchemaVersionNumber={'LatestVersion': True}
    )
    return response['SchemaDefinition']
```

### 2. API Gateways

Export AsyncAPI specs for API gateway configuration:

```python
def export_for_api_gateway(spec: Dict[str, Any]) -> Dict[str, Any]:
    """Convert AsyncAPI to API Gateway configuration"""
    
    gateway_config = {
        'routes': [],
        'subscriptions': []
    }
    
    for channel_id, channel in spec['channels'].items():
        gateway_config['routes'].append({
            'path': f"/events/{channel['address']}",
            'method': 'POST',
            'target': {
                'type': spec['servers']['kafka']['protocol'],
                'destination': channel['address']
            }
        })
    
    return gateway_config
```

### 3. Monitoring & Observability

Integrate with APM tools to track actual event flows:

```python
# Example: DataDog integration
from datadog import api, initialize

def compare_with_runtime_metrics(catalog_events, timeframe='1h'):
    """Compare discovered events with actual runtime metrics"""
    
    initialize(api_key=DD_API_KEY, app_key=DD_APP_KEY)
    
    for event in catalog_events:
        topic = event['channel_name']
        
        # Query DataDog for actual message volume
        query = f"sum:kafka.producer.message_rate{{topic:{topic}}}.rollup(sum, {timeframe})"
        result = api.Metric.query(start='-1h', end='now', query=query)
        
        if result['series']:
            event['runtime_metrics'] = {
                'message_count': sum(result['series'][0]['pointlist']),
                'last_seen': result['series'][0]['end']
            }
```

## Governance & Standards

### Catalog Policies

Define policies for event standards:

```yaml
# catalog-policies.yaml
policies:
  naming:
    pattern: "^[a-z]+\\.[a-z]+\\.[a-z]+$"  # domain.entity.action
    examples:
      - payment.transaction.created
      - order.item.updated
    
  schema:
    required_fields:
      - eventId
      - eventType
      - timestamp
      - version
    
  versioning:
    strategy: semantic
    breaking_changes_require: major_version_bump
```

### Validation Pipeline

```python
class CatalogValidator:
    def __init__(self, policies: Dict[str, Any]):
        self.policies = policies
    
    def validate_spec(self, spec: Dict[str, Any]) -> List[str]:
        """Validate spec against policies"""
        violations = []
        
        for channel_id, channel in spec['channels'].items():
            # Check naming convention
            if not re.match(self.policies['naming']['pattern'], channel['address']):
                violations.append(
                    f"Channel {channel['address']} doesn't match naming convention"
                )
        
        return violations
```

## Monitoring & Metrics

Track key metrics for the discovery system:

```python
# Key metrics to track
metrics = {
    'discovery': {
        'repositories_scanned': 0,
        'events_discovered': 0,
        'services_cataloged': 0,
        'execution_time_seconds': 0,
        'last_run_timestamp': None
    },
    'quality': {
        'schemas_enriched': 0,
        'validation_failures': 0,
        'stale_specs': 0  # Not updated in X days
    },
    'usage': {
        'catalog_views': 0,
        'spec_downloads': 0,
        'api_requests': 0
    }
}
```

## Troubleshooting

### Common Issues

**1. SourceGraph Rate Limiting**
```python
# Implement exponential backoff
async def search_with_retry(query, max_retries=3):
    for attempt in range(max_retries):
        try:
            return await sg_client.search(query)
        except RateLimitError:
            wait_time = 2 ** attempt
            await asyncio.sleep(wait_time)
    raise Exception("Max retries exceeded")
```

**2. Large Repository Processing**
```python
# Stream results instead of loading all at once
async def process_large_repo(repo_pattern):
    offset = 0
    batch_size = 100
    
    while True:
        results = await sg_client.search(
            f"repo:{repo_pattern}",
            limit=batch_size,
            offset=offset
        )
        
        if not results:
            break
            
        process_batch(results)
        offset += batch_size
```

**3. Incomplete Metadata**
```python
# Fallback strategies
def extract_metadata_with_fallbacks(result):
    metadata = primary_extractor.extract(result)
    
    if not metadata or metadata.get('channel_name') == 'unknown':
        # Try secondary extraction methods
        metadata = secondary_extractor.extract(result)
    
    if not metadata:
        # Log for manual review
        log_for_review(result)
        return None
    
    return metadata
```

## Success Metrics

Define clear success criteria:

- **Coverage**: 90%+ of services cataloged
- **Accuracy**: 95%+ detection accuracy
- **Freshness**: Catalog updated within 24 hours of code changes
- **Adoption**: 80%+ of teams using catalog
- **Quality**: 70%+ of specs have enriched schemas

## Cost Considerations

### Infrastructure Costs
- SourceGraph license: ~$50-100/developer/year
- Compute: $100-500/month (depending on scale)
- Storage: $10-50/month
- CI/CD: Included in existing platforms

### Time Investment
- Initial setup: 2-4 weeks (1 FTE)
- Ongoing maintenance: 4-8 hours/week
- Custom detector development: 2-4 hours per pattern

### ROI
- Reduced integration time: 20-30%
- Fewer production incidents: 15-25%
- Improved developer productivity: 10-20%
- Better architectural visibility: Invaluable

## Next Steps

1. **Week 1**: Set up development environment and run demo
2. **Week 2**: Configure for your SourceGraph instance
3. **Week 3**: Test with subset of applications
4. **Week 4**: Develop custom detectors for your patterns
5. **Week 5-8**: Scale to full organization
6. **Week 9-12**: Operationalize and integrate with workflows

## Support & Resources

- Internal wiki: [Link to your internal documentation]
- Slack channel: #asyncapi-catalog
- Office hours: Every Tuesday 2-3 PM
- Training materials: [Link to training]

## Appendix

### A. Complete SourceGraph Query Reference

```
# Kafka patterns
lang:java KafkaTemplate.send
lang:java Producer<.*>.send
lang:python kafka.produce

# RabbitMQ patterns
lang:java RabbitTemplate.convertAndSend
lang:python pika.basic_publish

# AWS patterns
lang:java AmazonSNS.publish
lang:python boto3.*sns.*publish
lang:typescript AWS.SNS.publish

# IBM MQ patterns
lang:java MQQueue.put
lang:java JmsTemplate.send.*mq
```

### B. Sample Output Formats

See the `demo_catalog/` directory for examples of:
- AsyncAPI YAML specifications
- Catalog index JSON
- Discovery reports
- Summary documentation