"""
Sourcegraph API client for repository scanning.

This module provides functionality to interact with Sourcegraph API
for code search and repository analysis.
"""

import logging
import requests
from typing import List, Dict, Any, Optional


logger = logging.getLogger(__name__)


class SourcegraphClient:
    """
    Client for interacting with Sourcegraph API.
    
    Provides methods to search code, retrieve repositories,
    and analyze code patterns across multiple repositories.
    """
    
    def __init__(self, config: Dict[str, Any]):
        """
        Initialize Sourcegraph client.
        
        Args:
            config: Configuration dictionary containing:
                - url: Sourcegraph instance URL
                - token: API access token
                - timeout: Request timeout in seconds (optional)
        """
        self.url = config.get('url', 'https://sourcegraph.com')
        self.token = config.get('token', '')
        self.timeout = config.get('timeout', 30)
        
        if not self.token:
            logger.warning("No Sourcegraph token provided, some features may be limited")
        
        self.session = requests.Session()
        if self.token:
            self.session.headers.update({
                'Authorization': f'token {self.token}'
            })
    
    def get_repositories(self, query: str = '') -> List[str]:
        """
        Get list of repositories to scan.
        
        Args:
            query: Optional search query to filter repositories
            
        Returns:
            List of repository names
        """
        logger.info("Fetching repositories from Sourcegraph")
        
        try:
            # GraphQL query to get repositories
            graphql_query = """
            query SearchRepositories($query: String!) {
                search(query: $query, version: V2) {
                    results {
                        repositories {
                            name
                        }
                    }
                }
            }
            """
            
            response = self.session.post(
                f"{self.url}/.api/graphql",
                json={
                    'query': graphql_query,
                    'variables': {'query': query or 'type:repo'}
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            repositories = [
                repo['name'] 
                for repo in data.get('data', {}).get('search', {}).get('results', {}).get('repositories', [])
            ]
            
            logger.info(f"Found {len(repositories)} repositories")
            return repositories
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching repositories: {e}")
            return []
    
    def search_code(self, query: str, repo: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Search for code patterns.
        
        Args:
            query: Search query (supports Sourcegraph search syntax)
            repo: Optional repository to limit search to
            
        Returns:
            List of search results with file paths and matches
        """
        if repo:
            query = f"repo:{repo} {query}"
        
        logger.debug(f"Searching code with query: {query}")
        
        try:
            graphql_query = """
            query SearchCode($query: String!) {
                search(query: $query, version: V2) {
                    results {
                        results {
                            ... on FileMatch {
                                file {
                                    path
                                    url
                                }
                                repository {
                                    name
                                }
                                lineMatches {
                                    lineNumber
                                    line
                                }
                            }
                        }
                    }
                }
            }
            """
            
            response = self.session.post(
                f"{self.url}/.api/graphql",
                json={
                    'query': graphql_query,
                    'variables': {'query': query}
                },
                timeout=self.timeout
            )
            response.raise_for_status()
            
            data = response.json()
            results = data.get('data', {}).get('search', {}).get('results', {}).get('results', [])
            
            logger.debug(f"Found {len(results)} code matches")
            return results
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error searching code: {e}")
            return []
    
    def get_file_content(self, repo: str, path: str, commit: str = 'HEAD') -> Optional[str]:
        """
        Get content of a specific file.
        
        Args:
            repo: Repository name
            path: File path within repository
            commit: Git commit/branch reference (default: HEAD)
            
        Returns:
            File content as string, or None if not found
        """
        try:
            # Use raw file API
            url = f"{self.url}/{repo}/-/raw/{commit}/{path}"
            response = self.session.get(url, timeout=self.timeout)
            response.raise_for_status()
            
            return response.text
            
        except requests.exceptions.RequestException as e:
            logger.error(f"Error fetching file {repo}/{path}: {e}")
            return None
