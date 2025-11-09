"""
AsyncAPI Discovery - Scan repositories for event producers and create AsyncAPI specifications.

This package provides tools to discover event producers in repositories and
generate AsyncAPI catalog specifications for them.
"""

__version__ = "0.1.0"
__author__ = "AsyncAPI Discovery Team"

from asyncapi_discovery.discovery import AsyncAPIDiscovery
from asyncapi_discovery.scanner import RepositoryScanner
from asyncapi_discovery.generator import AsyncAPIGenerator

__all__ = [
    "AsyncAPIDiscovery",
    "RepositoryScanner",
    "AsyncAPIGenerator",
]
