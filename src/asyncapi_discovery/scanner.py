"""
Repository scanner module for detecting event producers.

This module scans repositories to find event producers regardless of the broker type.
"""

from typing import Dict, List
from pathlib import Path
import re


class RepositoryScanner:
    """Scanner for detecting event producers in repositories."""

    def __init__(self, repository_path: str):
        """
        Initialize the repository scanner.

        Args:
            repository_path: Path to the repository to scan
        """
        self.repository_path = Path(repository_path)
        self.supported_extensions = ['.py', '.js', '.ts', '.java', '.go']

    def scan(self) -> Dict:
        """
        Scan the repository for event producers.

        Returns:
            Dictionary containing discovered event producers
        """
        producers = {
            'events': [],
            'files': [],
            'statistics': {
                'total_files_scanned': 0,
                'producers_found': 0
            }
        }

        for ext in self.supported_extensions:
            files = list(self.repository_path.rglob(f'*{ext}'))
            producers['statistics']['total_files_scanned'] += len(files)
            
            for file_path in files:
                if self._should_skip(file_path):
                    continue
                    
                events = self._scan_file(file_path)
                if events:
                    producers['events'].extend(events)
                    producers['files'].append(str(file_path))
                    producers['statistics']['producers_found'] += len(events)

        return producers

    def _should_skip(self, file_path: Path) -> bool:
        """
        Check if a file should be skipped during scanning.

        Args:
            file_path: Path to the file

        Returns:
            True if the file should be skipped, False otherwise
        """
        skip_patterns = [
            '/test/', '/tests/', '/__pycache__/', '/node_modules/', 
            '/venv/', '/.git/', '/dist/', '/build/'
        ]
        
        path_str = str(file_path)
        return any(pattern in path_str for pattern in skip_patterns)

    def _scan_file(self, file_path: Path) -> List[Dict]:
        """
        Scan a single file for event producers.

        Args:
            file_path: Path to the file to scan

        Returns:
            List of discovered events
        """
        events = []
        
        try:
            content = file_path.read_text(encoding='utf-8')
            
            # Look for common event producer patterns
            patterns = [
                r'publish\s*\(\s*["\']([^"\']+)["\']',
                r'send\s*\(\s*["\']([^"\']+)["\']',
                r'emit\s*\(\s*["\']([^"\']+)["\']',
                r'produce\s*\(\s*["\']([^"\']+)["\']',
            ]
            
            for pattern in patterns:
                matches = re.finditer(pattern, content)
                for match in matches:
                    event_name = match.group(1)
                    events.append({
                        'name': event_name,
                        'file': str(file_path),
                        'type': 'producer'
                    })
        
        except (UnicodeDecodeError, IOError):
            # Skip files that can't be read
            pass
        
        return events
