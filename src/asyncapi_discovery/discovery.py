"""
Main discovery module for AsyncAPI Discovery.

This module coordinates the scanning and generation process.
"""

from typing import Dict, List, Optional
from pathlib import Path

from asyncapi_discovery.scanner import RepositoryScanner
from asyncapi_discovery.generator import AsyncAPIGenerator


class AsyncAPIDiscovery:
    """Main class for discovering event producers and generating AsyncAPI specifications."""

    def __init__(self, repository_path: str):
        """
        Initialize the AsyncAPI Discovery.

        Args:
            repository_path: Path to the repository to scan
        """
        self.repository_path = Path(repository_path)
        self.scanner = RepositoryScanner(repository_path)
        self.generator = AsyncAPIGenerator()

    def discover(self) -> Dict:
        """
        Discover event producers in the repository.

        Returns:
            Dictionary containing discovered event producers
        """
        producers = self.scanner.scan()
        return producers

    def generate_spec(self, producers: Optional[Dict] = None) -> str:
        """
        Generate AsyncAPI specification from discovered producers.

        Args:
            producers: Optional dictionary of producers. If None, will run discovery first.

        Returns:
            AsyncAPI specification as YAML string
        """
        if producers is None:
            producers = self.discover()
        
        spec = self.generator.generate(producers)
        return spec

    def run(self, output_path: Optional[str] = None) -> str:
        """
        Run the complete discovery and generation process.

        Args:
            output_path: Optional path to save the generated specification

        Returns:
            Generated AsyncAPI specification
        """
        producers = self.discover()
        spec = self.generate_spec(producers)
        
        if output_path:
            output_file = Path(output_path)
            output_file.write_text(spec)
        
        return spec
