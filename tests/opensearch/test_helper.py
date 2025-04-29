import json
import pytest
import sys
from unittest.mock import patch, Mock

class TestOpenSearchHelper:
    def setup_method(self, method):
        """Setup that runs before each test method"""
        # Create mock client
        self.mock_client = Mock()
        
        # Mock the client module first
        mock_client_module = Mock()
        mock_client_module.client = self.mock_client
        sys.modules['opensearch.client'] = mock_client_module

        # Import after mocking
        from opensearch.helper import (
            list_indices,
            get_index_mapping,
            search_index,
            get_shards
        )
        
        # Store functions
        self.list_indices = list_indices
        self.get_index_mapping = get_index_mapping
        self.search_index = search_index
        self.get_shards = get_shards

    def teardown_method(self, method):
        """Cleanup after each test method"""
        sys.modules.pop('opensearch.client', None)

    def test_list_indices(self):
        """Test list_indices function"""
        # Setup mock response
        mock_response = [
            {"index": "index1", "health": "green", "status": "open"},
            {"index": "index2", "health": "yellow", "status": "open"}
        ]
        self.mock_client.cat.indices.return_value = mock_response

        # Execute
        result = self.list_indices()

        # Assert
        assert result == mock_response
        self.mock_client.cat.indices.assert_called_once_with(format="json")

    @patch('opensearch.helper.client')
    def test_get_index_mapping(self, mock_client):
        """Test get_index_mapping function"""
        # Setup mock response
        mock_response = {
            "test-index": {
                "mappings": {
                    "properties": {
                        "field1": {"type": "text"},
                        "field2": {"type": "keyword"}
                    }
                }
            }
        }
        mock_client.indices.get_mapping.return_value = mock_response

        # Execute
        result = self.get_index_mapping("test-index")

        # Assert
        assert result == mock_response
        mock_client.indices.get_mapping.assert_called_once_with(index="test-index")

    @patch('opensearch.helper.client')
    def test_search_index(self, mock_client):
        """Test search_index function"""
        # Setup mock response
        mock_response = {
            "hits": {
                "total": {"value": 1},
                "hits": [
                    {
                        "_index": "test-index",
                        "_id": "1",
                        "_source": {"field": "value"}
                    }
                ]
            }
        }
        mock_client.search.return_value = mock_response

        # Setup test query
        test_query = {"query": {"match_all": {}}}

        # Execute
        result = self.search_index("test-index", test_query)

        # Assert
        assert result == mock_response
        mock_client.search.assert_called_once_with(
            index="test-index",
            body=test_query
        )

    @patch('opensearch.helper.client')
    def test_get_shards(self, mock_client):
        """Test get_shards function"""
        # Setup mock response
        mock_response = [
            {
                "index": "test-index",
                "shard": "0",
                "prirep": "p",
                "state": "STARTED",
                "docs": "1000",
                "store": "1mb",
                "ip": "127.0.0.1",
                "node": "node1"
            }
        ]
        mock_client.cat.shards.return_value = mock_response

        # Execute
        result = self.get_shards("test-index")

        # Assert
        assert result == mock_response
        mock_client.cat.shards.assert_called_once_with(
            index="test-index",
            format="json"
        )

    @patch('opensearch.helper.client')
    def test_list_indices_error(self, mock_client):
        """Test list_indices error handling"""
        # Setup mock to raise exception
        mock_client.cat.indices.side_effect = Exception("Connection error")

        # Execute and assert
        with pytest.raises(Exception) as exc_info:
            self.list_indices()
        assert str(exc_info.value) == "Connection error"

    @patch('opensearch.helper.client')
    def test_get_index_mapping_error(self, mock_client):
        """Test get_index_mapping error handling"""
        # Setup mock to raise exception
        mock_client.indices.get_mapping.side_effect = Exception("Index not found")

        # Execute and assert
        with pytest.raises(Exception) as exc_info:
            self.get_index_mapping("non-existent-index")
        assert str(exc_info.value) == "Index not found"

    @patch('opensearch.helper.client')
    def test_search_index_error(self, mock_client):
        """Test search_index error handling"""
        # Setup mock to raise exception
        mock_client.search.side_effect = Exception("Invalid query")

        # Execute and assert
        with pytest.raises(Exception) as exc_info:
            self.search_index("test-index", {"invalid": "query"})
        assert str(exc_info.value) == "Invalid query"

    @patch('opensearch.helper.client')
    def test_get_shards_error(self, mock_client):
        """Test get_shards error handling"""
        # Setup mock to raise exception
        mock_client.cat.shards.side_effect = Exception("Shard not found")

        # Execute and assert
        with pytest.raises(Exception) as exc_info:
            self.get_shards("non-existent-index")
        assert str(exc_info.value) == "Shard not found"
