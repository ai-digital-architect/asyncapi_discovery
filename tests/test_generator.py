"""Tests for the generator module."""

import pytest
import yaml

from asyncapi_discovery.generator import AsyncAPIGenerator


class TestAsyncAPIGenerator:
    """Test cases for AsyncAPIGenerator class."""

    def test_generator_initialization(self):
        """Test generator initialization."""
        generator = AsyncAPIGenerator()
        assert generator.asyncapi_version == "2.6.0"

    def test_generate_empty_spec(self):
        """Test generating specification with no producers."""
        generator = AsyncAPIGenerator()
        producers = {'events': [], 'files': [], 'statistics': {}}
        
        spec_yaml = generator.generate(producers)
        spec = yaml.safe_load(spec_yaml)
        
        assert 'asyncapi' in spec
        assert spec['asyncapi'] == "2.6.0"
        assert 'info' in spec
        assert 'channels' in spec

    def test_generate_with_events(self):
        """Test generating specification with discovered events."""
        generator = AsyncAPIGenerator()
        producers = {
            'events': [
                {'name': 'user.created', 'file': 'test.py', 'type': 'producer'},
                {'name': 'order.placed', 'file': 'test.py', 'type': 'producer'}
            ],
            'files': ['test.py'],
            'statistics': {'producers_found': 2}
        }
        
        spec_yaml = generator.generate(producers)
        spec = yaml.safe_load(spec_yaml)
        
        assert 'channels' in spec
        assert 'user.created' in spec['channels']
        assert 'order.placed' in spec['channels']

    def test_create_base_spec(self):
        """Test creating base specification structure."""
        generator = AsyncAPIGenerator()
        base_spec = generator._create_base_spec()
        
        assert base_spec['asyncapi'] == "2.6.0"
        assert 'info' in base_spec
        assert 'title' in base_spec['info']
        assert 'servers' in base_spec

    def test_create_channel(self):
        """Test creating channel definition."""
        generator = AsyncAPIGenerator()
        event = {'name': 'test.event', 'file': 'test.py', 'type': 'producer'}
        
        channel = generator._create_channel(event)
        
        assert 'description' in channel
        assert 'subscribe' in channel
        assert 'message' in channel['subscribe']
