"""
Command-line interface for AsyncAPI Discovery.

This module provides the CLI for running AsyncAPI discovery operations.
"""

import sys
import argparse
from pathlib import Path

from asyncapi_discovery.discovery import AsyncAPIDiscovery


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(
        description='Discover event producers and generate AsyncAPI specifications'
    )
    
    parser.add_argument(
        'repository',
        type=str,
        help='Path to the repository to scan'
    )
    
    parser.add_argument(
        '-o', '--output',
        type=str,
        help='Output file path for the AsyncAPI specification',
        default='asyncapi.yaml'
    )
    
    parser.add_argument(
        '--discover-only',
        action='store_true',
        help='Only discover producers without generating specification'
    )
    
    parser.add_argument(
        '-v', '--verbose',
        action='store_true',
        help='Enable verbose output'
    )
    
    args = parser.parse_args()
    
    # Validate repository path
    repo_path = Path(args.repository)
    if not repo_path.exists():
        print(f"Error: Repository path '{args.repository}' does not exist", file=sys.stderr)
        sys.exit(1)
    
    if not repo_path.is_dir():
        print(f"Error: Repository path '{args.repository}' is not a directory", file=sys.stderr)
        sys.exit(1)
    
    try:
        discovery = AsyncAPIDiscovery(args.repository)
        
        if args.discover_only:
            # Only discover producers
            producers = discovery.discover()
            print(f"Found {producers['statistics']['producers_found']} producers")
            print(f"Scanned {producers['statistics']['total_files_scanned']} files")
            
            if args.verbose:
                print("\nDiscovered events:")
                for event in producers['events']:
                    print(f"  - {event['name']} in {event['file']}")
        else:
            # Run full discovery and generation
            if args.verbose:
                print(f"Scanning repository: {args.repository}")
            
            spec = discovery.run(args.output)
            
            print(f"AsyncAPI specification generated: {args.output}")
            
            if args.verbose:
                print("\nGenerated specification:")
                print(spec)
    
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        if args.verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


if __name__ == '__main__':
    main()
