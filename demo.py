#!/usr/bin/env python3
"""
Demo script for AsyncAPI Discovery tool.

This script demonstrates the basic usage of the AsyncAPI Discovery tool
with example configurations and mock data.
"""

import json
import logging
import sys
from typing import Dict, Any, List


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


class MockSourcegraphClient:
    """Mock Sourcegraph client for demonstration purposes."""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        logger.info("Initialized mock Sourcegraph client")
    
    def get_repositories(self) -> List[str]:
        """Return mock list of repositories."""
        return [
            "example/user-service",
            "example/order-service",
            "example/notification-service"
        ]
    
    def search_code(self, query: str, repo: str = None) -> List[Dict[str, Any]]:
        """Return mock search results."""
        # Simulate finding Kafka producer
        if 'KafkaProducer' in query or '.send' in query:
            return [{
                'file': {'path': 'src/main/java/com/example/EventProducer.java'},
                'repository': {'name': repo or 'example/user-service'},
                'lineMatches': [
                    {
                        'lineNumber': 42,
                        'line': 'producer.send("user.created", userEvent);'
                    }
                ]
            }]
        
        # Simulate finding RabbitMQ publisher
        if 'RabbitTemplate' in query or 'basic_publish' in query:
            return [{
                'file': {'path': 'src/services/order_service.py'},
                'repository': {'name': repo or 'example/order-service'},
                'lineMatches': [
                    {
                        'lineNumber': 78,
                        'line': 'channel.basic_publish(exchange="orders", routing_key="order.placed", body=message)'
                    }
                ]
            }]
        
        return []


def create_demo_config() -> Dict[str, Any]:
    """Create a demonstration configuration."""
    return {
        "sourcegraph": {
            "url": "https://sourcegraph.com",
            "token": "demo-token-not-real",
            "timeout": 30
        },
        "event_detection": {
            "brokers": ["kafka", "rabbitmq", "aws", "pubsub"],
            "exclude_patterns": ["test", "mock"]
        },
        "output": {
            "directory": "demo_catalog",
            "format": "json"
        }
    }


def demo_event_detection():
    """Demonstrate event detection functionality."""
    logger.info("=== AsyncAPI Discovery Demo ===")
    logger.info("")
    
    # Create demo configuration
    config = create_demo_config()
    logger.info("Configuration:")
    logger.info(json.dumps(config, indent=2))
    logger.info("")
    
    # Initialize mock client
    client = MockSourcegraphClient(config['sourcegraph'])
    
    # Get repositories
    logger.info("Fetching repositories...")
    repos = client.get_repositories()
    logger.info(f"Found {len(repos)} repositories:")
    for repo in repos:
        logger.info(f"  - {repo}")
    logger.info("")
    
    # Search for events
    logger.info("Searching for event producers...")
    
    for repo in repos:
        logger.info(f"Scanning {repo}:")
        
        # Search for Kafka patterns
        kafka_results = client.search_code('KafkaProducer', repo)
        if kafka_results:
            logger.info(f"  Found Kafka producer:")
            for result in kafka_results:
                for match in result['lineMatches']:
                    logger.info(f"    Line {match['lineNumber']}: {match['line']}")
        
        # Search for RabbitMQ patterns
        rabbitmq_results = client.search_code('RabbitTemplate', repo)
        if rabbitmq_results:
            logger.info(f"  Found RabbitMQ publisher:")
            for result in rabbitmq_results:
                for match in result['lineMatches']:
                    logger.info(f"    Line {match['lineNumber']}: {match['line']}")
        
        logger.info("")
    
    # Summary
    logger.info("=== Demo Summary ===")
    logger.info("The AsyncAPI Discovery tool can:")
    logger.info("  1. Connect to Sourcegraph to search code repositories")
    logger.info("  2. Detect event producers across different brokers:")
    logger.info("     - Apache Kafka")
    logger.info("     - RabbitMQ")
    logger.info("     - AWS SNS/SQS")
    logger.info("     - Google Pub/Sub")
    logger.info("     - Azure Service Bus")
    logger.info("     - Generic event emitters")
    logger.info("  3. Generate AsyncAPI specifications for discovered events")
    logger.info("  4. Create a catalog of all event-driven APIs")
    logger.info("")
    logger.info("To use the real tool:")
    logger.info("  1. Configure your Sourcegraph instance in config.json")
    logger.info("  2. Run: python main.py")
    logger.info("  3. Review generated AsyncAPI specs in asyncapi_catalog/")


def main() -> int:
    """Run the demonstration."""
    try:
        demo_event_detection()
        return 0
    except Exception as e:
        logger.error(f"Demo failed: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
