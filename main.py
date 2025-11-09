#!/usr/bin/env python3
"""
Main entry point for AsyncAPI Discovery tool.

This module orchestrates the discovery of event producers in repositories
and generates AsyncAPI catalog specifications.
"""

import argparse
import json
import logging
import sys
from typing import Optional

from sourcegraph_client import SourcegraphClient
from event_detector import EventDetector
from catalog_manager import CatalogManager


# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)


def load_config(config_path: str = "config.json") -> dict:
    """
    Load configuration from JSON file.
    
    Args:
        config_path: Path to configuration file
        
    Returns:
        Configuration dictionary
    """
    try:
        with open(config_path, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        sys.exit(1)
    except json.JSONDecodeError as e:
        logger.error(f"Invalid JSON in configuration file: {e}")
        sys.exit(1)


def parse_args() -> argparse.Namespace:
    """Parse command line arguments."""
    parser = argparse.ArgumentParser(
        description='Discover event producers and generate AsyncAPI specifications'
    )
    parser.add_argument(
        '--config',
        default='config.json',
        help='Path to configuration file (default: config.json)'
    )
    parser.add_argument(
        '--repository',
        help='Specific repository to scan (optional)'
    )
    parser.add_argument(
        '--output',
        default='asyncapi_catalog',
        help='Output directory for AsyncAPI specifications (default: asyncapi_catalog)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    return parser.parse_args()


def main() -> int:
    """
    Main application logic.
    
    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    args = parse_args()
    
    if args.verbose:
        logging.getLogger().setLevel(logging.DEBUG)
    
    logger.info("Starting AsyncAPI Discovery")
    
    # Load configuration
    config = load_config(args.config)
    logger.debug(f"Loaded configuration: {config}")
    
    # Initialize components
    sourcegraph_client = SourcegraphClient(config.get('sourcegraph', {}))
    event_detector = EventDetector(config.get('event_detection', {}))
    catalog_manager = CatalogManager(args.output)
    
    try:
        # Get repositories to scan
        if args.repository:
            repositories = [args.repository]
        else:
            repositories = sourcegraph_client.get_repositories()
        
        logger.info(f"Scanning {len(repositories)} repositories")
        
        # Process each repository
        for repo in repositories:
            logger.info(f"Processing repository: {repo}")
            
            # Detect events in repository
            events = event_detector.detect_events(repo, sourcegraph_client)
            
            if events:
                logger.info(f"Found {len(events)} events in {repo}")
                
                # Generate AsyncAPI specification
                catalog_manager.add_specification(repo, events)
            else:
                logger.info(f"No events found in {repo}")
        
        # Save catalog
        catalog_manager.save()
        logger.info(f"AsyncAPI catalog saved to {args.output}")
        
        return 0
        
    except Exception as e:
        logger.error(f"Error during execution: {e}", exc_info=True)
        return 1


if __name__ == '__main__':
    sys.exit(main())
