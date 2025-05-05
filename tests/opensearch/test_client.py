# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import os
import pytest
import sys
from opensearchpy import OpenSearch, RequestsHttpConnection
from requests_aws4auth import AWS4Auth
from unittest.mock import Mock

class TestOpenSearchClient:
    def setup_method(self, method):
        """Setup that runs before each test method"""
        # Mock AWS4Auth
        self.mock_aws4auth = Mock()
        mock_aws4auth_module = Mock()
        mock_aws4auth_module.AWS4Auth = self.mock_aws4auth
        sys.modules['requests_aws4auth'] = mock_aws4auth_module

        # Mock OpenSearch
        self.mock_opensearch = Mock()
        mock_opensearch_module = Mock()
        mock_opensearch_module.OpenSearch = self.mock_opensearch
        mock_opensearch_module.RequestsHttpConnection = RequestsHttpConnection
        sys.modules['opensearchpy'] = mock_opensearch_module

        # Set environment variables
        self.env_vars = {
            'OPENSEARCH_URL': 'https://test-domain.amazonaws.com',
            'OPENSEARCH_USERNAME': 'user',
            'OPENSEARCH_PASSWORD': 'pass',
            'AWS_REGION': 'us-west-2',
            'AWS_ACCESS_KEY': 'test-key',
            'AWS_SECRET_ACCESS_KEY': 'test-secret',
            'AWS_SESSION_TOKEN': 'test-token'
        }
        for key, value in self.env_vars.items():
            os.environ[key] = value

    def teardown_method(self, method):
        """Cleanup after each test method"""
        # Clean up module mocks
        sys.modules.pop('requests_aws4auth', None)
        sys.modules.pop('opensearchpy', None)
        sys.modules.pop('opensearch.client', None)

        # Clean up environment variables
        for key in self.env_vars:
            os.environ.pop(key, None)

    def test_initialize_client_non_aws(self):
        """Test client initialization for non-AWS OpenSearch"""
        # Update environment for non AWS
        os.environ['OPENSEARCH_URL'] = 'https://non-aws-host:9200'

        from opensearch.client import initialize_client

        # Assert
        self.mock_opensearch.assert_called_once()
        args = self.mock_opensearch.call_args[1]
        
        assert args['hosts'] == ['https://non-aws-host:9200']
        assert args['use_ssl'] is True
        assert args['verify_certs'] is True
        assert args['connection_class'] == RequestsHttpConnection
        assert args['http_auth'] == ('user', 'pass')

    def test_initialize_client_aws_with_basic_auth(self):
        """Test client initialization for AWS OpenSearch with basic authentication"""
        from opensearch.client import initialize_client

        # Assert
        self.mock_opensearch.assert_called_once()
        args = self.mock_opensearch.call_args[1]
        
        assert args['hosts'] == ['https://test-domain.amazonaws.com']
        assert args['use_ssl'] is True
        assert args['verify_certs'] is True
        assert args['connection_class'] == RequestsHttpConnection
        assert args['http_auth'] == ('user', 'pass')
    
    def test_initialize_client_aws_with_iam_auth(self):
        """Test client initialization for AWS OpenSearch with IAM authentication"""
        # Update environment to remove username and password
        os.environ['OPENSEARCH_USERNAME'] = ''
        os.environ['OPENSEARCH_PASSWORD'] = ''

        # Import after environment update
        from opensearch.client import initialize_client

        # Assert
        self.mock_opensearch.assert_called_once()
        args = self.mock_opensearch.call_args[1]
        
        assert args['hosts'] == ['https://test-domain.amazonaws.com']
        assert args['use_ssl'] is True
        assert args['verify_certs'] is True
        assert args['connection_class'] == RequestsHttpConnection
        assert isinstance(args['http_auth'], Mock)

    def test_initialize_client_custom_port(self):
        """Test client initialization with custom port"""
        # Update environment for custom port
        os.environ['OPENSEARCH_URL'] = 'https://custom-domain:1234'

        # Import after environment update
        from opensearch.client import initialize_client

        # Assert
        self.mock_opensearch.assert_called_once()
        args = self.mock_opensearch.call_args[1]
        
        assert args['hosts'] == ['https://custom-domain:1234']
        assert args['use_ssl'] is True
        assert args['verify_certs'] is True
        assert args['connection_class'] == RequestsHttpConnection
        assert args['http_auth'] == ('user', 'pass')

    def test_initialize_client_no_ssl(self):
        """Test client initialization without SSL"""
        # Update environment for non-SSL
        os.environ['OPENSEARCH_URL'] = 'http://localhost:9200'
        
        # Import after environment update
        from opensearch.client import initialize_client

        # Assert
        self.mock_opensearch.assert_called_once()
        args = self.mock_opensearch.call_args[1]
        
        assert args['hosts'] == ['http://localhost:9200']
        assert args['use_ssl'] is False
        assert args['verify_certs'] is True
        assert args['connection_class'] == RequestsHttpConnection
        assert args['http_auth'] == ('user', 'pass')

    def test_initialize_client_empty_url(self):
        """Test client initialization with empty URL"""
        # Remove URL from environment
        os.environ.pop('OPENSEARCH_URL', None)

        # Execute and assert
        with pytest.raises(ValueError) as exc_info:
            from opensearch.client import initialize_client
        assert str(exc_info.value) == "OPENSEARCH_URL environment variable is not set"
