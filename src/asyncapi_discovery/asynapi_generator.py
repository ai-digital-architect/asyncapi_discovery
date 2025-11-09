"""
AsyncAPI Generator - Generates AsyncAPI 3.0 specifications
Converts discovered event metadata into valid AsyncAPI documents
"""

import logging
from typing import Dict, List, Any
from datetime import datetime

logger = logging.getLogger(__name__)


class AsyncAPIGenerator:
    """Generates AsyncAPI 3.0 specifications from event metadata"""
    
    def __init__(self):
        self.version = "3.0.0"
    
    def generate_spec(
        self,
        service_name: str,
        events: List[Dict[str, Any]],
        version: str = "1.0.0"
    ) -> Dict[str, Any]:
        """
        Generate complete AsyncAPI 3.0 specification for a service
        
        Args:
            service_name: Name of the service/application
            events: List of event metadata dictionaries
            version: API version
            
        Returns:
            AsyncAPI 3.0 specification as dictionary
        """
        logger.info(f"Generating AsyncAPI spec for {service_name} with {len(events)} events")
        
        spec = {
            "asyncapi": self.version,
            "info": self._generate_info(service_name, events, version),
            "servers": self._generate_servers(events),
            "channels": self._generate_channels(events),
            "operations": self._generate_operations(events),
            "components": self._generate_components(events)
        }
        
        return spec
    
    def _generate_info(
        self,
        service_name: str,
        events: List[Dict[str, Any]],
        version: str
    ) -> Dict[str, Any]:
        """Generate info section"""
        # Get unique repositories
        repos = list(set(e.get('repository', '') for e in events))
        
        return {
            "title": f"{service_name} Event API",
            "version": version,
            "description": (
                f"Asynchronous event API for {service_name}. "
                f"This specification was auto-generated from code analysis."
            ),
            "x-generated": {
                "timestamp": datetime.utcnow().isoformat() + "Z",
                "eventCount": len(events),
                "repositories": repos
            }
        }
    
    def _generate_servers(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate servers section based on brokers used"""
        servers = {}
        
        # Group events by broker
        brokers = {}
        for event in events:
            broker = event.get('broker', 'unknown')
            if broker not in brokers:
                brokers[broker] = []
            brokers[broker].append(event)
        
        # Create server entries
        for broker, broker_events in brokers.items():
            server_config = self._get_server_config(broker, broker_events)
            servers[broker] = server_config
        
        return servers
    
    def _get_server_config(
        self,
        broker: str,
        events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Generate server configuration for a specific broker"""
        
        config = {
            "host": "{environment}.example.com",  # Placeholder
            "protocol": self._get_protocol(broker),
            "description": f"{broker.upper()} message broker",
            "variables": {
                "environment": {
                    "default": "dev",
                    "enum": ["dev", "staging", "prod"]
                }
            }
        }
        
        # Add broker-specific configurations
        if broker == 'kafka':
            config["bindings"] = {
                "kafka": {
                    "schemaRegistryUrl": "https://schema-registry.example.com"
                }
            }
        elif broker == 'rabbitmq':
            config["bindings"] = {
                "amqp": {
                    "exchange": "default"
                }
            }
        elif broker.startswith('aws-'):
            config["bindings"] = {
                "aws": {
                    "region": "us-east-1"
                }
            }
        
        return config
    
    def _get_protocol(self, broker: str) -> str:
        """Map broker to protocol"""
        protocol_map = {
            'kafka': 'kafka',
            'rabbitmq': 'amqp',
            'aws-sns': 'sns',
            'aws-sqs': 'sqs',
            'aws-eventbridge': 'eventbridge',
            'ibm-mq': 'ibmmq'
        }
        return protocol_map.get(broker, 'unknown')
    
    def _generate_channels(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate channels section"""
        channels = {}
        
        # Group events by channel
        channel_groups = {}
        for event in events:
            channel_name = event.get('channel_name', 'unknown')
            if channel_name not in channel_groups:
                channel_groups[channel_name] = []
            channel_groups[channel_name].append(event)
        
        # Create channel entries
        for channel_name, channel_events in channel_groups.items():
            # Sanitize channel name for AsyncAPI
            channel_id = self._sanitize_channel_id(channel_name)
            channels[channel_id] = self._create_channel(channel_name, channel_events)
        
        return channels
    
    def _sanitize_channel_id(self, channel_name: str) -> str:
        """Convert channel name to valid AsyncAPI channel ID"""
        # Replace special characters with underscores
        sanitized = channel_name.replace('/', '_').replace('.', '_').replace(':', '_')
        return sanitized
    
    def _create_channel(
        self,
        channel_name: str,
        events: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Create channel definition"""
        first_event = events[0]
        broker = first_event.get('broker', 'unknown')
        channel_type = first_event.get('channel_type', 'topic')
        
        channel = {
            "address": channel_name,
            "description": f"Channel: {channel_name}",
            "messages": {}
        }
        
        # Add messages
        for idx, event in enumerate(events):
            message_id = f"{self._sanitize_channel_id(channel_name)}_message_{idx}"
            channel["messages"][message_id] = {
                "$ref": f"#/components/messages/{message_id}"
            }
        
        # Add broker-specific bindings
        if broker == 'kafka':
            channel["bindings"] = {
                "kafka": {
                    "topic": channel_name,
                    "partitions": 3,
                    "replicas": 2
                }
            }
        elif broker == 'rabbitmq':
            parts = channel_name.split('/')
            channel["bindings"] = {
                "amqp": {
                    "is": channel_type,
                    "exchange": {
                        "name": parts[0] if len(parts) > 1 else "default",
                        "type": "topic"
                    },
                    "queue": {
                        "name": parts[1] if len(parts) > 1 else channel_name
                    }
                }
            }
        
        return channel
    
    def _generate_operations(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate operations section"""
        operations = {}
        
        # Create operation for each unique channel
        channel_operations = {}
        for event in events:
            channel_name = event.get('channel_name', 'unknown')
            channel_id = self._sanitize_channel_id(channel_name)
            operation = event.get('operation', 'send')
            
            if channel_id not in channel_operations:
                channel_operations[channel_id] = {
                    'channel': channel_name,
                    'operation': operation,
                    'events': []
                }
            channel_operations[channel_id]['events'].append(event)
        
        # Create operation entries
        for channel_id, op_data in channel_operations.items():
            operation_id = f"{op_data['operation']}_{channel_id}"
            operations[operation_id] = {
                "action": op_data['operation'],
                "channel": {
                    "$ref": f"#/channels/{channel_id}"
                },
                "description": f"{op_data['operation'].capitalize()} messages to {op_data['channel']}",
                "messages": [
                    {"$ref": f"#/channels/{channel_id}/messages/{channel_id}_message_{idx}"}
                    for idx in range(len(op_data['events']))
                ]
            }
        
        return operations
    
    def _generate_components(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Generate components section"""
        messages = {}
        schemas = {}
        
        # Create message components
        for event in events:
            channel_name = event.get('channel_name', 'unknown')
            channel_id = self._sanitize_channel_id(channel_name)
            message_type = event.get('message_type', 'Unknown')
            
            # Create unique message ID
            event_idx = [e for e in events if e.get('channel_name') == channel_name].index(event)
            message_id = f"{channel_id}_message_{event_idx}"
            
            # Create schema ID
            schema_id = f"{message_id}_payload"
            
            messages[message_id] = {
                "name": message_type,
                "title": f"{message_type} Event",
                "summary": f"Message published to {channel_name}",
                "contentType": "application/json",
                "payload": {
                    "$ref": f"#/components/schemas/{schema_id}"
                },
                "x-source": {
                    "repository": event.get('repository', ''),
                    "filePath": event.get('file_path', ''),
                    "lineNumber": event.get('line_number', 0)
                }
            }
            
            # Create basic schema
            schemas[schema_id] = self._create_schema(event)
        
        return {
            "messages": messages,
            "schemas": schemas
        }
    
    def _create_schema(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Create JSON schema for message payload"""
        message_type = event.get('message_type', 'Unknown')
        
        return {
            "type": "object",
            "title": message_type,
            "description": f"Schema for {message_type} (to be enriched with actual fields)",
            "properties": {
                "eventId": {
                    "type": "string",
                    "description": "Unique event identifier",
                    "format": "uuid"
                },
                "timestamp": {
                    "type": "string",
                    "description": "Event timestamp",
                    "format": "date-time"
                },
                "eventType": {
                    "type": "string",
                    "description": "Type of event",
                    "const": message_type
                },
                "payload": {
                    "type": "object",
                    "description": "Event-specific payload (schema to be defined)",
                    "additionalProperties": True
                }
            },
            "required": ["eventId", "timestamp", "eventType"],
            "x-note": "This is a template schema. Actual schema should be enriched with real payload fields."
        }