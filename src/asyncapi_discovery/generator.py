"""
AsyncAPI specification generator module.

This module generates AsyncAPI specifications from discovered event producers.
"""

from typing import Dict, List
import yaml


class AsyncAPIGenerator:
    """Generator for creating AsyncAPI specifications."""

    def __init__(self):
        """Initialize the AsyncAPI generator."""
        self.asyncapi_version = "2.6.0"

    def generate(self, producers: Dict) -> str:
        """
        Generate AsyncAPI specification from discovered producers.

        Args:
            producers: Dictionary containing discovered event producers

        Returns:
            AsyncAPI specification as YAML string
        """
        spec = self._create_base_spec()
        
        # Add channels for each discovered event
        channels = {}
        for event in producers.get('events', []):
            channel_name = event.get('name', 'unknown')
            if channel_name not in channels:
                channels[channel_name] = self._create_channel(event)
        
        spec['channels'] = channels
        
        return yaml.dump(spec, default_flow_style=False, sort_keys=False)

    def _create_base_spec(self) -> Dict:
        """
        Create the base AsyncAPI specification structure.

        Returns:
            Base specification dictionary
        """
        return {
            'asyncapi': self.asyncapi_version,
            'info': {
                'title': 'Discovered AsyncAPI Specification',
                'version': '1.0.0',
                'description': 'Auto-generated AsyncAPI specification from repository scanning'
            },
            'servers': {
                'development': {
                    'url': 'localhost',
                    'protocol': 'amqp',
                    'description': 'Development server'
                }
            }
        }

    def _create_channel(self, event: Dict) -> Dict:
        """
        Create a channel definition for an event.

        Args:
            event: Event information dictionary

        Returns:
            Channel specification dictionary
        """
        return {
            'description': f'Channel for {event.get("name", "unknown")} event',
            'subscribe': {
                'summary': f'Subscribe to {event.get("name", "unknown")} events',
                'message': {
                    'name': event.get('name', 'unknown'),
                    'title': event.get('name', 'Unknown Event'),
                    'contentType': 'application/json',
                    'payload': {
                        'type': 'object',
                        'properties': {
                            'eventId': {
                                'type': 'string',
                                'description': 'Unique event identifier'
                            },
                            'timestamp': {
                                'type': 'string',
                                'format': 'date-time',
                                'description': 'Event timestamp'
                            },
                            'data': {
                                'type': 'object',
                                'description': 'Event payload data'
                            }
                        }
                    }
                }
            }
        }
