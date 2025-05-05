# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

from opensearchpy import OpenSearch, RequestsHttpConnection
from urllib.parse import urlparse
from requests_aws4auth import AWS4Auth
import os
import boto3

# This file should expose the OpenSearch py client
def initialize_client() -> OpenSearch:
    AWS_DOMAINS = ("amazonaws.com", ".aws")

    opensearch_url = os.getenv("OPENSEARCH_URL", "")
    opensearch_username = os.getenv("OPENSEARCH_USERNAME", "")
    opensearch_password = os.getenv("OPENSEARCH_PASSWORD", "")
    aws_region = os.getenv("AWS_REGION", "")
    aws_access_key = os.getenv("AWS_ACCESS_KEY", "")
    aws_secret_access_key = os.getenv("AWS_SECRET_ACCESS_KEY", "")
    aws_session_token = os.getenv("AWS_SESSION_TOKEN", "")

    if not opensearch_url:
        raise ValueError("OPENSEARCH_URL environment variable is not set")

    # Parse the OpenSearch domain URL
    parsed_url = urlparse(opensearch_url)
    is_aos = any(domain in opensearch_url for domain in AWS_DOMAINS)

    # Common client configuration
    client_kwargs: Dict[str, Any] = {
        'hosts': [opensearch_url],
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