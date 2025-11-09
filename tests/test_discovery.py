"""Tests for the discovery module."""

import pytest
from pathlib import Path
import tempfile

from asyncapi_discovery.discovery import AsyncAPIDiscovery


class TestAsyncAPIDiscovery:
    """Test cases for AsyncAPIDiscovery class."""

    def test_discovery_initialization(self):
        """Test discovery initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            discovery = AsyncAPIDiscovery(tmpdir)
            assert discovery.repository_path == Path(tmpdir)
            assert discovery.scanner is not None
            assert discovery.generator is not None

    def test_discover(self):
        """Test discover method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            discovery = AsyncAPIDiscovery(tmpdir)
            result = discovery.discover()
            
            assert 'events' in result
            assert 'files' in result
            assert 'statistics' in result

    def test_generate_spec(self):
        """Test generate_spec method."""
        with tempfile.TemporaryDirectory() as tmpdir:
            discovery = AsyncAPIDiscovery(tmpdir)
            producers = {
                'events': [{'name': 'test.event', 'file': 'test.py', 'type': 'producer'}],
                'files': ['test.py'],
                'statistics': {'producers_found': 1}
            }
            
            spec = discovery.generate_spec(producers)
            
            assert isinstance(spec, str)
            assert 'asyncapi' in spec
            assert 'test.event' in spec

    def test_run_without_output(self):
        """Test run method without output file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            discovery = AsyncAPIDiscovery(tmpdir)
            spec = discovery.run()
            
            assert isinstance(spec, str)
            assert 'asyncapi' in spec

    def test_run_with_output(self):
        """Test run method with output file."""
        with tempfile.TemporaryDirectory() as tmpdir:
            output_path = Path(tmpdir) / "output.yaml"
            discovery = AsyncAPIDiscovery(tmpdir)
            spec = discovery.run(str(output_path))
            
            assert output_path.exists()
            assert output_path.read_text() == spec
