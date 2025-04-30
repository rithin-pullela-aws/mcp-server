from opensearchpy import OpenSearch, RequestsHttpConnection
from urllib.parse import urlparse
from requests_aws4auth import AWS4Auth
import os
import boto3

# This file should expose the OpenSearch py client
def initialize_client() -> OpenSearch:
    AWS_DOMAIN = "amazonaws.com"

    opensearch_url = os.getenv("OPENSEARCH_URL", "")
    opensearch_username = os.getenv("OPENSEARCH_USERNAME", "")
    opensearch_password = os.getenv("OPENSEARCH_PASSWORD", "")
    aws_region = os.getenv("AWS_REGION", "")
    aws_access_key = os.getenv("AWS_ACCESS_KEY", "")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_session_token = os.getenv("AWS_SESSION_TOKEN", "")

    if not opensearch_url:
        raise ValueError("OPENSEARCH_URL environment variable is not set")

    # Parse the OpenSearch domain URL to extract host and port
    parsed_url = urlparse(opensearch_url)
    host = parsed_url.hostname

    if not host:
        raise ValueError(f"Invalid OpenSearch URL: {opensearch_url}")
        
    is_aos = AWS_DOMAIN in host
    port = parsed_url.port or (443 if is_aos else 9200)

    # Common client configuration
    client_kwargs: Dict[str, Any] = {
        'hosts': [{"host": host, "port": port}],
        'use_ssl': (parsed_url.scheme == "https"),
        'verify_certs': True,
        'connection_class': RequestsHttpConnection,
    }

    # Configure authentication based on domain type
    if is_aos:
        # Use basic authentication if username and password are provided
        if opensearch_username and opensearch_password:
            client_kwargs['http_auth'] = (opensearch_username, opensearch_password)
            return OpenSearch(**client_kwargs)
        
        # Create AWS4Auth for IAM authentication
        aws_auth = AWS4Auth(
            aws_access_key,
            aws_secret_access_key,
            aws_region,
            'es',
            session_token=aws_session_token
        )
        client_kwargs['http_auth'] = aws_auth
    else:
        # Non-AWS domain - use basic authentication
        client_kwargs['http_auth'] = (opensearch_username, opensearch_password)

    return OpenSearch(**client_kwargs)

client = initialize_client()