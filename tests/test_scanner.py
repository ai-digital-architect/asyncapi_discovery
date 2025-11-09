"""Tests for the scanner module."""

import pytest
from pathlib import Path
import tempfile
import os

from asyncapi_discovery.scanner import RepositoryScanner


class TestRepositoryScanner:
    """Test cases for RepositoryScanner class."""

    def test_scanner_initialization(self):
        """Test scanner initialization."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = RepositoryScanner(tmpdir)
            assert scanner.repository_path == Path(tmpdir)
            assert len(scanner.supported_extensions) > 0

    def test_scan_empty_directory(self):
        """Test scanning an empty directory."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = RepositoryScanner(tmpdir)
            result = scanner.scan()
            
            assert 'events' in result
            assert 'files' in result
            assert 'statistics' in result
            assert result['statistics']['total_files_scanned'] == 0
            assert result['statistics']['producers_found'] == 0

    def test_scan_with_event_producer(self):
        """Test scanning a directory with event producer code."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Create a test file with event producer pattern
            test_file = Path(tmpdir) / "producer.py"
            test_file.write_text('publish("user.created")')
            
            scanner = RepositoryScanner(tmpdir)
            result = scanner.scan()
            
            assert result['statistics']['total_files_scanned'] > 0
            assert len(result['events']) > 0
            assert result['events'][0]['name'] == 'user.created'

    def test_should_skip_test_files(self):
        """Test that test files are skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = RepositoryScanner(tmpdir)
            test_path = Path(tmpdir) / "tests" / "test_example.py"
            assert scanner._should_skip(test_path) is True

    def test_should_not_skip_regular_files(self):
        """Test that regular files are not skipped."""
        with tempfile.TemporaryDirectory() as tmpdir:
            scanner = RepositoryScanner(tmpdir)
            regular_path = Path(tmpdir) / "src" / "module.py"
            assert scanner._should_skip(regular_path) is False
