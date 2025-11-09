#!/usr/bin/env python3
"""
Demo Script - Demonstrates the AsyncAPI discovery system with mock data
This shows how the system works without needing actual SourceGraph access
"""

import asyncio
import json
from pathlib import Path

from event_detector import EventDetectorRegistry
from asyncapi_generator import AsyncAPIGenerator
from catalog_manager import CatalogManager


def generate_mock_search_results():
    """Generate mock search results simulating SourceGraph findings"""
    return [
        # Kafka Spring Boot example
        {
            'repository': 'github.com/yourorg/payment-service',
            'file_path': 'src/main/java/com/company/payment/EventPublisher.java',
            'line_number': 45,
            'code_snippet': 'kafkaTemplate.send("payment.processed", paymentEvent);',
            'repository_url': 'https://github.com/yourorg/payment-service'
        },
        {
            'repository': 'github.com/yourorg/payment-service',
            'file_path': 'src/main/java/com/company/payment/EventPublisher.java',
            'line_number': 67,
            'code_snippet': 'kafkaTemplate.send("payment.failed", failureEvent);',
            'repository_url': 'https://github.com/yourorg/payment-service'
        },
        # RabbitMQ example
        {
            'repository': 'github.com/yourorg/order-service',
            'file_path': 'src/main/java/com/company/order/messaging/OrderEventPublisher.java',
            'line_number': 32,
            'code_snippet': 'rabbitTemplate.convertAndSend("order.exchange", "order.created", orderDto);',
            'repository_url': 'https://github.com/yourorg/order-service'
        },
        # AWS SNS example
        {
            'repository': 'github.com/yourorg/notification-service',
            'file_path': 'src/main/java/com/company/notification/SnsPublisher.java',
            'line_number': 28,
            'code_snippet': 'snsClient.publish(builder -> builder.topicArn("arn:aws:sns:us-east-1:123456789:user-notifications"));',
            'repository_url': 'https://github.com/yourorg/notification-service'
        },
        # EventBridge example
        {
            'repository': 'github.com/yourorg/analytics-service',
            'file_path': 'src/main/java/com/company/analytics/EventBridgePublisher.java',
            'line_number': 55,
            'code_snippet': 'eventBridgeClient.putEvents(request -> request.eventBusName("analytics-events").detailType("UserAction"));',
            'repository_url': 'https://github.com/yourorg/analytics-service'
        },
        # Another Kafka example
        {
            'repository': 'github.com/yourorg/inventory-service',
            'file_path': 'src/main/java/com/company/inventory/StockEventProducer.java',
            'line_number': 41,
            'code_snippet': 'kafkaTemplate.send("inventory.updated", inventoryEvent);',
            'repository_url': 'https://github.com/yourorg/inventory-service'
        },
        # SQS example
        {
            'repository': 'github.com/yourorg/fulfillment-service',
            'file_path': 'src/main/java/com/company/fulfillment/QueuePublisher.java',
            'line_number': 19,
            'code_snippet': 'sqsClient.sendMessage(builder -> builder.queueUrl("https://sqs.us-east-1.amazonaws.com/123456789/fulfillment-queue"));',
            'repository_url': 'https://github.com/yourorg/fulfillment-service'
        },
    ]


async def run_demo():
    """Run the demo with mock data"""
    print("=" * 80)
    print("AsyncAPI Discovery System - Demo Mode")
    print("=" * 80)
    print()
    
    # Initialize components
    detector_registry = EventDetectorRegistry()
    asyncapi_generator = AsyncAPIGenerator()
    catalog_manager = CatalogManager(output_dir='./demo_catalog')
    
    print("Step 1: Simulating SourceGraph queries...")
    print(f"  - Registered {len(detector_registry.get_all_queries())} detector queries")
    mock_results = generate_mock_search_results()
    print(f"  - Found {len(mock_results)} code matches\n")
    
    print("Step 2: Extracting event metadata...")
    events = []
    for result in mock_results:
        # Determine which detector to use based on code snippet
        if 'kafkaTemplate' in result['code_snippet']:
            detector = detector_registry.get_detector('kafka', 'spring-kafka')
        elif 'rabbitTemplate' in result['code_snippet']:
            detector = detector_registry.get_detector('rabbitmq', 'spring-amqp')
        elif 'snsClient' in result['code_snippet']:
            detector = detector_registry.get_detector('aws-sns', 'aws-sdk')
        elif 'sqsClient' in result['code_snippet']:
            detector = detector_registry.get_detector('aws-sqs', 'aws-sdk')
        elif 'eventBridgeClient' in result['code_snippet']:
            detector = detector_registry.get_detector('aws-eventbridge', 'aws-sdk')
        else:
            continue
        
        metadata = detector.extract_metadata(result)
        if metadata:
            events.append(metadata)
            print(f"  ✓ {metadata['service_name']}: {metadata['channel_name']} ({metadata['broker']})")
    
    print(f"\n  Total events extracted: {len(events)}\n")
    
    print("Step 3: Grouping events by service...")
    events_by_service = {}
    for event in events:
        service = event['service_name']
        if service not in events_by_service:
            events_by_service[service] = []
        events_by_service[service].append(event)
    
    for service, service_events in events_by_service.items():
        print(f"  - {service}: {len(service_events)} events")
    print()
    
    print("Step 4: Generating AsyncAPI 3.0 specifications...")
    specs = []
    for service_name, service_events in events_by_service.items():
        spec = asyncapi_generator.generate_spec(
            service_name=service_name,
            events=service_events,
            version="1.0.0"
        )
        specs.append({
            'service': service_name,
            'spec': spec
        })
        
        # Show spec summary
        channel_count = len(spec['channels'])
        operation_count = len(spec['operations'])
        print(f"  ✓ {service_name}: {channel_count} channels, {operation_count} operations")
    
    print()
    
    print("Step 5: Saving to catalog...")
    catalog_manager.save_catalog(specs)
    report = catalog_manager.generate_report(events, specs)
    
    print(f"  ✓ Saved {len(specs)} specifications")
    print(f"  ✓ Generated catalog index")
    print(f"  ✓ Created discovery report\n")
    
    print("=" * 80)
    print("Demo Complete!")
    print("=" * 80)
    print(f"\nResults saved to: {report['output_directory']}")
    print("\nCatalog structure:")
    print("  demo_catalog/")
    print("  ├── specs/                    # AsyncAPI specifications (YAML & JSON)")
    print("  ├── reports/                  # Discovery reports")
    print("  ├── catalog-index.json       # Catalog index")
    print("  └── SUMMARY.txt              # Human-readable summary")
    print()
    print("Summary:")
    print(f"  - Events discovered: {report['summary']['total_events']}")
    print(f"  - Services cataloged: {report['summary']['total_services']}")
    print(f"  - Repositories scanned: {report['summary']['total_repositories']}")
    print()
    print("Brokers detected:")
    for broker, count in report['brokers'].items():
        print(f"  - {broker}: {count} events")
    print()
    
    # Show a sample spec
    if specs:
        print("Sample AsyncAPI Specification Preview:")
        print("-" * 80)
        sample_spec = specs[0]['spec']
        print(f"Service: {sample_spec['info']['title']}")
        print(f"Version: {sample_spec['info']['version']}")
        print(f"Channels: {', '.join(list(sample_spec['channels'].keys())[:3])}")
        print(f"Operations: {len(sample_spec['operations'])}")
        print()


if __name__ == "__main__":
    asyncio.run(run_demo())