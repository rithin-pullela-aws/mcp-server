# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import json
import pytest
import sys
from unittest.mock import patch, Mock

class TestTools():
    def setup_method(self):
        """Setup that runs before each test method"""
        # Mock OpenSearch modules
        self.mock_client = Mock()
        sys.modules['opensearch.client'] = Mock(client=self.mock_client)
        sys.modules['opensearch.helper'] = Mock(
            list_indices=Mock(return_value=[]),
            get_index_mapping=Mock(return_value={}),
            search_index=Mock(return_value={}),
            get_shards=Mock(return_value=[])
        )

        # Import after mocking
        from tools.tools import (
            ListIndicesArgs,
            GetIndexMappingArgs,
            SearchIndexArgs,
            GetShardsArgs,
            list_indices_tool,
            get_index_mapping_tool,
            search_index_tool,
            get_shards_tool,
            TOOL_REGISTRY
        )
        
        # Store the imports as instance attributes
        self.ListIndicesArgs = ListIndicesArgs
        self.GetIndexMappingArgs = GetIndexMappingArgs
        self.SearchIndexArgs = SearchIndexArgs
        self.GetShardsArgs = GetShardsArgs
        self.TOOL_REGISTRY = TOOL_REGISTRY
        
        # Store the tool functions
        self._list_indices_tool = list_indices_tool
        self._get_index_mapping_tool = get_index_mapping_tool
        self._search_index_tool = search_index_tool
        self._get_shards_tool = get_shards_tool

        # Setup patches
        self.patcher_list_indices = patch('tools.tools.list_indices')
        self.patcher_get_mapping = patch('tools.tools.get_index_mapping')
        self.patcher_search = patch('tools.tools.search_index')
        self.patcher_shards = patch('tools.tools.get_shards')

        # Start patches
        self.mock_list_indices = self.patcher_list_indices.start()
        self.mock_get_mapping = self.patcher_get_mapping.start()
        self.mock_search = self.patcher_search.start()
        self.mock_shards = self.patcher_shards.start()

    def teardown_method(self):
        """Cleanup after each test method"""
        # Stop all patches
        self.patcher_list_indices.stop()
        self.patcher_get_mapping.stop()
        self.patcher_search.stop()
        self.patcher_shards.stop()

        # Clean up module mocks
        sys.modules.pop('opensearch.client', None)
        sys.modules.pop('opensearch.helper', None)

    @pytest.mark.asyncio
    async def test_list_indices_tool(self):
        """Test list_indices_tool successful"""
        # Setup
        self.mock_list_indices.return_value = [
            {'index': 'index1'},
            {'index': 'index2'}
        ]

        # Execute
        result = await self._list_indices_tool(self.ListIndicesArgs())

        # Assert
        assert len(result) == 1
        assert result[0]['type'] == 'text'
        assert 'index1\nindex2' in result[0]['text']

    @pytest.mark.asyncio
    async def test_list_indices_tool_error(self):
        """Test list_indices_tool exception handling"""
        # Setup
        self.mock_list_indices.side_effect = Exception("Test error")

        # Execute
        result = await self._list_indices_tool(self.ListIndicesArgs())

        # Assert
        assert len(result) == 1
        assert result[0]['type'] == 'text'
        assert 'Error listing indices: Test error' in result[0]['text']

    @pytest.mark.asyncio
    async def test_get_index_mapping_tool(self):
        """Test get_index_mapping_tool successful"""
        # Setup
        mock_mapping = {
            "mappings": {
                "properties": {
                    "field1": {"type": "text"}
                }
            }
        }
        self.mock_get_mapping.return_value = mock_mapping

        # Execute
        result = await self._get_index_mapping_tool(self.GetIndexMappingArgs(index="test-index"))

        # Assert
        assert len(result) == 1
        assert result[0]['type'] == 'text'
        assert 'Mapping for test-index' in result[0]['text']
        assert json.loads(result[0]['text'].split('\n', 1)[1]) == mock_mapping
    
    @pytest.mark.asyncio
    async def test_get_index_mapping_tool_error(self):
        """Test get_index_mapping_tool exception handling"""
        # Setup
        self.mock_get_mapping.side_effect = Exception("Test error")

        # Execute
        result = await self._get_index_mapping_tool(self.GetIndexMappingArgs(index="test-index"))

        # Assert
        assert len(result) == 1
        assert result[0]['type'] == 'text'
        assert 'Error getting mapping: Test error' in result[0]['text']

    @pytest.mark.asyncio
    async def test_search_index_tool(self):
        """Test search_index_tool successful"""
        # Setup
        mock_results = {
            "hits": {
                "total": {"value": 1},
                "hits": [{"_source": {"field": "value"}}]
            }
        }
        self.mock_search.return_value = mock_results

        # Execute
        result = await self._search_index_tool(self.SearchIndexArgs(
            index="test-index",
            query={"match_all": {}}
        ))

        # Assert
        assert len(result) == 1
        assert result[0]['type'] == 'text'
        assert 'Search results from test-index' in result[0]['text']
        assert json.loads(result[0]['text'].split('\n', 1)[1]) == mock_results
    
    @pytest.mark.asyncio
    async def test_search_index_tool_error(self):
        """Test search_index_tool exception handling"""
        # Setup
        self.mock_search.side_effect = Exception("Test error")

        # Execute
        result = await self._search_index_tool(self.SearchIndexArgs(
            index="test-index",
            query={"match_all": {}}
        ))

        # Assert
        assert len(result) == 1
        assert result[0]['type'] == 'text'
        assert 'Error searching index: Test error' in result[0]['text']

    @pytest.mark.asyncio
    async def test_get_shards_tool(self):
        """Test get_shards_tool successful"""
        # Setup
        mock_shards = [{
            "index": "test-index",
            "shard": "0",
            "prirep": "p",
            "state": "STARTED",
            "docs": "1000",
            "store": "1mb",
            "ip": "127.0.0.1",
            "node": "node1"
        }]
        self.mock_shards.return_value = mock_shards

        # Execute
        result = await self._get_shards_tool(self.GetShardsArgs(index="test-index"))

        # Assert
        assert len(result) == 1
        assert result[0]['type'] == 'text'
        assert 'index | shard | prirep | state | docs | store | ip | node' in result[0]['text']
        assert 'test-index | 0 | p | STARTED | 1000 | 1mb | 127.0.0.1 | node1' in result[0]['text']

    @pytest.mark.asyncio
    async def test_get_shards_tool_error(self):
        """Test get_shards_tool exception handling"""
        # Setup
        self.mock_shards.side_effect = Exception("Test error")

        # Execute
        result = await self._get_shards_tool(self.GetShardsArgs(index="test-index"))

        # Assert
        assert len(result) == 1
        assert result[0]['type'] == 'text'
        assert 'Error getting shards information: Test error' in result[0]['text']

    def test_tool_registry(self):
        """Test TOOL_REGISTRY structure"""
        expected_tools = ["list_indices", "get_index_mapping", "search_index", "get_shards"]
        
        for tool in expected_tools:
            assert tool in self.TOOL_REGISTRY
            assert "description" in self.TOOL_REGISTRY[tool]
            assert "input_schema" in self.TOOL_REGISTRY[tool]
            assert "function" in self.TOOL_REGISTRY[tool]
            assert "args_model" in self.TOOL_REGISTRY[tool]

    def test_input_models(self):
        """Test input models validation"""
        with pytest.raises(ValueError):
            self.GetIndexMappingArgs()  # Should fail without index

        with pytest.raises(ValueError):
            self.SearchIndexArgs(index="test")  # Should fail without query

        # Test valid inputs
        assert self.GetIndexMappingArgs(index="test").index == "test"
        assert self.SearchIndexArgs(index="test", query={"match": {}}).index == "test"
        assert self.GetShardsArgs(index="test").index == "test"
        assert isinstance(self.ListIndicesArgs(), self.ListIndicesArgs)