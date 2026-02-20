"""Elasticsearch/OpenSearch client and connection manager."""

from typing import Optional, Union, Any

try:
    from elasticsearch import Elasticsearch
    from elasticsearch.exceptions import ConnectionError as ESConnectionError
except ImportError:
    Elasticsearch = None
    ESConnectionError = Exception

try:
    from opensearchpy import OpenSearch
except ImportError:
    OpenSearch = None

from src.utils.config import settings
from src.utils.logger import logger


class ElasticsearchClient:
    """Manages Elasticsearch/OpenSearch connection and operations."""
    
    def __init__(
        self,
        host: str = None,
        port: int = None,
        username: str = None,
        password: str = None
    ):
        """Initialize Client.
        
        Args:
            host: Host URL
            port: Port
            username: Username for authentication
            password: Password for authentication
        """
        self.host = host or settings.elasticsearch_host
        self.port = port or settings.elasticsearch_port
        self.username = username or settings.elasticsearch_user
        self.password = password or settings.elasticsearch_password
        
        # Build URL
        if self.host.startswith('http'):
            self.url = self.host
        elif self.port == 443 and 'localhost' not in self.host:
             self.url = f"https://{self.host}"
        else:
             self.url = f"http://{self.host}:{self.port}"
             
        self._client: Optional[Union[Elasticsearch, OpenSearch]] = None
        self._is_opensearch = False
        
    @property
    def client(self) -> Union[Elasticsearch, OpenSearch]:
        """Get or create client instance.
        """
        if self._client is None:
            self._connect()
        return self._client
    
    def _connect(self):
        """Establish connection."""
        try:
            logger.info(f"Connecting to Search Engine at {self.url}...")
            
            # --- Attempt 1: OpenSearch (Preferred for Bonsai) ---
            if OpenSearch:
                try:
                    logger.info("Attempting connection with OpenSearch client...")
                    # Basic Auth for OpenSearch
                    auth = None
                    if self.username and self.password:
                        auth = (self.username, self.password)
                    
                    os_client = OpenSearch(
                        hosts=[self.url],
                        http_auth=auth,
                        use_ssl=self.url.startswith('https'),
                        verify_certs=True,
                        ssl_assert_hostname=False,
                        ssl_show_warn=False,
                        timeout=30
                    )
                    
                    if os_client.ping():
                        info = os_client.info()
                        version = info['version']['number']
                        dist = info['version'].get('distribution', 'elasticsearch')
                        logger.info(f"✅ Connected to OpenSearch/Elasticsearch {version} ({dist})")
                        self._client = os_client
                        self._is_opensearch = True
                        return
                    else:
                         logger.warning("OpenSearch ping failed.")
                except Exception as e:
                    logger.warning(f"OpenSearch connection attempt failed: {e}")

            # --- Attempt 2: Elasticsearch (Fallback) ---
            if Elasticsearch:
                logger.info("Attempting connection with Elasticsearch client...")
                # Basic Auth for Elasticsearch
                basic_auth = None
                if self.username and self.password:
                    basic_auth = (self.username, self.password)
                
                es_client = Elasticsearch(
                    hosts=[self.url],
                    basic_auth=basic_auth,
                    verify_certs=False, # Often needed for older ES/Bonsai
                    ssl_show_warn=False,
                    request_timeout=30
                )
                
                if es_client.ping():
                    info = es_client.info()
                    version = info['version']['number']
                    logger.info(f"✅ Connected to Elasticsearch {version}")
                    self._client = es_client
                    self._is_opensearch = False
                    return
                else:
                    logger.error("Elasticsearch ping failed.")
            
            raise Exception("Could not connect to search engine with either client.")
                
        except Exception as e:
            logger.error(f"Failed to connect to Search Engine: {e}", exc_info=True)
            raise
    
    def is_connected(self) -> bool:
        """Check if connected."""
        try:
            return self.client.ping()
        except:
            return False
    
    def close(self):
        """Close connection."""
        if self._client:
            self._client.close()
            self._client = None
            logger.info("Connection closed")
    
    def get_cluster_health(self) -> dict:
        """Get cluster health."""
        return self.client.cluster.health()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
