"""
HTTP connection pool implementation for the TTS system.

This module provides HTTP connection pooling functionality for improved performance.
Layer 2 - Core Services: Depends only on Layer 1 (Foundation) and external libraries.
"""

import requests
from modules.types.protocols import ConnectionPoolProtocol


class ConnectionPool(ConnectionPoolProtocol):
    """HTTP connection pool for better performance"""
    
    def __init__(self, base_url: str, pool_size: int = 5):
        """
        Initialize connection pool.
        
        Args:
            base_url: Base URL for requests
            pool_size: Maximum number of connections in pool
        """
        self.base_url = base_url
        self.session = requests.Session()
        adapter = requests.adapters.HTTPAdapter(
            pool_connections=pool_size,
            pool_maxsize=pool_size,
            max_retries=requests.adapters.Retry(
                total=3,
                backoff_factor=0.3,
                status_forcelist=[500, 502, 503, 504]
            )
        )
        self.session.mount("http://", adapter)
        self.session.mount("https://", adapter)
    
    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """GET request with connection pooling"""
        url = f"{self.base_url}{endpoint}"
        return self.session.get(url, **kwargs)
    
    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """POST request with connection pooling"""
        url = f"{self.base_url}{endpoint}"
        return self.session.post(url, **kwargs)
    
    def close(self) -> None:
        """Close all connections"""
        self.session.close()