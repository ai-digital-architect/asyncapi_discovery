"""
Event detection module for discovering event producers.

This module analyzes code to identify event-driven patterns
across different messaging systems and brokers.
"""

import logging
import re
from typing import List, Dict, Any, Set, Optional


logger = logging.getLogger(__name__)


class EventDetector:
    """
    Detects event producers in code regardless of the broker.
    
    Supports detection of various event-driven patterns including:
    - Kafka producers
    - RabbitMQ publishers
    - AWS SNS/SQS
    - Google Pub/Sub
    - Azure Service Bus
    - Custom event emitters
    """
    
    # Patterns for detecting different event producers
    KAFKA_PATTERNS = [
        r'KafkaProducer',
        r'\.send\s*\(',
        r'kafka\.Producer',
        r'@KafkaListener',
    ]
    
    RABBITMQ_PATTERNS = [
        r'channel\.basic_publish',
        r'RabbitTemplate',
        r'@RabbitListener',
        r'pika\.BlockingConnection',
    ]
    
    AWS_PATTERNS = [
        r'sns\.publish',
        r'sqs\.send_message',
        r'boto3\.client\(["\']sns["\']',
        r'boto3\.client\(["\']sqs["\']',
    ]
    
    PUBSUB_PATTERNS = [
        r'publisher\.publish',
        r'google\.cloud\.pubsub',
        r'PublisherClient',
    ]
    
    AZURE_PATTERNS = [
        r'ServiceBusClient',
        r'send_messages',
        r'azure\.servicebus',
    ]
    
    GENERIC_EVENT_PATTERNS = [
        r'\.emit\s*\(',
        r'\.publish\s*\(',
        r'\.fire\s*\(',
        r'EventEmitter',
        r'\.trigger\s*\(',
    ]
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize event detector.
        
        Args:
            config: Configuration dictionary with detection settings
        """
        self.config = config
        self.patterns = self._compile_patterns()
    
    def _compile_patterns(self) -> Dict[str, List[re.Pattern]]:
        """Compile regex patterns for efficient matching."""
        return {
            'kafka': [re.compile(p, re.IGNORECASE) for p in self.KAFKA_PATTERNS],
            'rabbitmq': [re.compile(p, re.IGNORECASE) for p in self.RABBITMQ_PATTERNS],
            'aws': [re.compile(p, re.IGNORECASE) for p in self.AWS_PATTERNS],
            'pubsub': [re.compile(p, re.IGNORECASE) for p in self.PUBSUB_PATTERNS],
            'azure': [re.compile(p, re.IGNORECASE) for p in self.AZURE_PATTERNS],
            'generic': [re.compile(p, re.IGNORECASE) for p in self.GENERIC_EVENT_PATTERNS],
        }
    
    def detect_events(self, repo: str, sourcegraph_client) -> List[Dict[str, Any]]:
        """
        Detect events in a repository.
        
        Args:
            repo: Repository name
            sourcegraph_client: SourcegraphClient instance for code search
            
        Returns:
            List of detected events with metadata
        """
        logger.info(f"Detecting events in repository: {repo}")
        
        events = []
        
        # Search for each pattern type
        for broker_type, patterns in self.patterns.items():
            for pattern in patterns:
                # Convert regex pattern to Sourcegraph query
                query = pattern.pattern
                results = sourcegraph_client.search_code(query, repo)
                
                for result in results:
                    event = self._parse_event(result, broker_type)
                    if event:
                        events.append(event)
        
        # Deduplicate events
        events = self._deduplicate_events(events)
        
        logger.info(f"Detected {len(events)} unique events in {repo}")
        return events
    
    def _parse_event(self, match: Dict[str, Any], broker_type: str) -> Optional[Dict[str, Any]]:
        """
        Parse code match to extract event information.
        
        Args:
            match: Code match from Sourcegraph
            broker_type: Type of message broker detected
            
        Returns:
            Event information dictionary
        """
        try:
            file_path = match.get('file', {}).get('path', '')
            repo_name = match.get('repository', {}).get('name', '')
            line_matches = match.get('lineMatches', [])
            
            if not line_matches:
                return None
            
            # Extract event name/topic from the code
            event_name = self._extract_event_name(line_matches, broker_type)
            
            return {
                'name': event_name,
                'broker': broker_type,
                'file': file_path,
                'repository': repo_name,
                'lines': [lm.get('lineNumber', 0) for lm in line_matches],
                'source_code': [lm.get('line', '') for lm in line_matches],
            }
            
        except Exception as e:
            logger.error(f"Error parsing event: {e}")
            return None
    
    def _extract_event_name(self, line_matches: List[Dict[str, Any]], broker_type: str) -> str:
        """
        Extract event/topic name from code lines.
        
        Args:
            line_matches: List of matching code lines
            broker_type: Type of message broker
            
        Returns:
            Extracted event name or default name
        """
        # Try to extract topic/event name from common patterns
        for match in line_matches:
            line = match.get('line', '')
            
            # Look for string literals that might be topic/event names
            string_pattern = r'["\']([a-zA-Z0-9._-]+)["\']'
            strings = re.findall(string_pattern, line)
            
            if strings:
                # Return first reasonable-looking string
                for s in strings:
                    if len(s) > 2 and not s.startswith('_'):
                        return s
        
        # Default name if extraction fails
        return f"{broker_type}_event"
    
    def _deduplicate_events(self, events: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Remove duplicate events based on name and broker.
        
        Args:
            events: List of events
            
        Returns:
            Deduplicated list of events
        """
        seen: Set[tuple] = set()
        unique_events = []
        
        for event in events:
            key = (event['name'], event['broker'])
            if key not in seen:
                seen.add(key)
                unique_events.append(event)
        
        return unique_events
