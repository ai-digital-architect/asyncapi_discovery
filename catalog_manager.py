"""
AsyncAPI catalog manager for generating and managing specifications.

This module handles the creation and organization of AsyncAPI
specification files for discovered events.
"""

import json
import logging
import os
from datetime import datetime
from typing import List, Dict, Any, Optional
from pathlib import Path


logger = logging.getLogger(__name__)


class CatalogManager:
    """
    Manages AsyncAPI catalog and specification generation.
    
    Creates AsyncAPI specification files for discovered events
    and maintains a catalog of all specifications.
    """
    
    ASYNCAPI_VERSION = "2.6.0"
    
    def __init__(self, output_dir: str = "asyncapi_catalog"):
        """
        Initialize catalog manager.
        
        Args:
            output_dir: Directory to save AsyncAPI specifications
        """
        self.output_dir = Path(output_dir)
        self.specifications: Dict[str, Dict[str, Any]] = {}
        
        # Create output directory if it doesn't exist
        self.output_dir.mkdir(parents=True, exist_ok=True)
        logger.info(f"Catalog output directory: {self.output_dir}")
    
    def add_specification(self, repo: str, events: List[Dict[str, Any]]) -> None:
        """
        Add AsyncAPI specification for a repository.
        
        Args:
            repo: Repository name
            events: List of detected events
        """
        logger.info(f"Creating AsyncAPI specification for {repo}")
        
        spec = self._create_specification(repo, events)
        self.specifications[repo] = spec
    
    def _create_specification(self, repo: str, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Create AsyncAPI specification document.
        
        Args:
            repo: Repository name
            events: List of events
            
        Returns:
            AsyncAPI specification dictionary
        """
        # Extract repository name for cleaner titles
        repo_name = repo.split('/')[-1] if '/' in repo else repo
        
        spec = {
            "asyncapi": self.ASYNCAPI_VERSION,
            "info": {
                "title": f"{repo_name} Event API",
                "version": "1.0.0",
                "description": f"AsyncAPI specification for event producers in {repo}",
                "contact": {
                    "name": "AsyncAPI Discovery Tool",
                    "url": "https://github.com/ai-digital-architect/asyncapi_discovery"
                }
            },
            "servers": {},
            "channels": {},
            "components": {
                "messages": {},
                "schemas": {}
            }
        }
        
        # Group events by broker
        brokers = self._group_events_by_broker(events)
        
        # Add servers for each broker type
        for broker_type, broker_events in brokers.items():
            server_name = f"{broker_type}_server"
            spec["servers"][server_name] = {
                "url": f"{broker_type}://localhost",
                "protocol": broker_type,
                "description": f"{broker_type.upper()} broker"
            }
        
        # Add channels and messages for each event
        for event in events:
            channel_name = event['name']
            message_name = f"{event['name']}_message"
            
            # Add channel
            spec["channels"][channel_name] = {
                "description": f"Event channel for {event['name']}",
                "subscribe": {
                    "operationId": f"subscribe_{event['name']}",
                    "summary": f"Subscribe to {event['name']} events",
                    "message": {
                        "$ref": f"#/components/messages/{message_name}"
                    }
                }
            }
            
            # Add message definition
            spec["components"]["messages"][message_name] = {
                "name": event['name'],
                "title": f"{event['name']} Event",
                "summary": f"Event produced from {event['file']}",
                "contentType": "application/json",
                "payload": {
                    "$ref": f"#/components/schemas/{event['name']}_payload"
                }
            }
            
            # Add schema (basic placeholder)
            spec["components"]["schemas"][f"{event['name']}_payload"] = {
                "type": "object",
                "properties": {
                    "eventId": {
                        "type": "string",
                        "description": "Unique event identifier"
                    },
                    "timestamp": {
                        "type": "string",
                        "format": "date-time",
                        "description": "Event timestamp"
                    },
                    "data": {
                        "type": "object",
                        "description": "Event payload data"
                    }
                }
            }
        
        return spec
    
    def _group_events_by_broker(self, events: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Group events by broker type.
        
        Args:
            events: List of events
            
        Returns:
            Dictionary mapping broker type to list of events
        """
        brokers: Dict[str, List[Dict[str, Any]]] = {}
        
        for event in events:
            broker = event.get('broker', 'generic')
            if broker not in brokers:
                brokers[broker] = []
            brokers[broker].append(event)
        
        return brokers
    
    def save(self) -> None:
        """Save all specifications to disk."""
        logger.info(f"Saving {len(self.specifications)} specifications")
        
        # Save individual specifications
        for repo, spec in self.specifications.items():
            self._save_specification(repo, spec)
        
        # Save catalog index
        self._save_catalog_index()
    
    def _save_specification(self, repo: str, spec: Dict[str, Any]) -> None:
        """
        Save a single AsyncAPI specification.
        
        Args:
            repo: Repository name
            spec: AsyncAPI specification
        """
        # Create safe filename from repository name
        filename = repo.replace('/', '_').replace('\\', '_') + '.json'
        filepath = self.output_dir / filename
        
        try:
            with open(filepath, 'w') as f:
                json.dump(spec, f, indent=2)
            logger.info(f"Saved specification: {filepath}")
            
            # Also save YAML version
            self._save_yaml_specification(filepath.with_suffix('.yaml'), spec)
            
        except Exception as e:
            logger.error(f"Error saving specification for {repo}: {e}")
    
    def _save_yaml_specification(self, filepath: Path, spec: Dict[str, Any]) -> None:
        """
        Save specification in YAML format.
        
        Args:
            filepath: Path to save YAML file
            spec: AsyncAPI specification
        """
        try:
            # Try to import yaml, but don't fail if not available
            import yaml
            with open(filepath, 'w') as f:
                yaml.dump(spec, f, default_flow_style=False, sort_keys=False)
            logger.info(f"Saved YAML specification: {filepath}")
        except ImportError:
            logger.debug("PyYAML not available, skipping YAML output")
        except Exception as e:
            logger.error(f"Error saving YAML specification: {e}")
    
    def _save_catalog_index(self) -> None:
        """Save catalog index with metadata about all specifications."""
        index = {
            "generated_at": datetime.utcnow().isoformat() + 'Z',
            "total_specifications": len(self.specifications),
            "specifications": []
        }
        
        for repo, spec in self.specifications.items():
            index["specifications"].append({
                "repository": repo,
                "title": spec["info"]["title"],
                "version": spec["info"]["version"],
                "channels": len(spec.get("channels", {})),
                "file": repo.replace('/', '_').replace('\\', '_') + '.json'
            })
        
        index_path = self.output_dir / "catalog_index.json"
        
        try:
            with open(index_path, 'w') as f:
                json.dump(index, f, indent=2)
            logger.info(f"Saved catalog index: {index_path}")
        except Exception as e:
            logger.error(f"Error saving catalog index: {e}")
