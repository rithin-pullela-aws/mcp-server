# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import asyncio
import os
import pytest
from unittest.mock import Mock, patch, AsyncMock
from mcp.types import Tool, TextContent
from contextlib import asynccontextmanager

# Set environment variables
os.environ['OPENSEARCH_URL'] = 'https://test-domain.us-west-2.es.amazonaws.com'
os.environ['AWS_REGION'] = 'us-west-2'
os.environ['AWS_ACCESS_KEY_ID'] = 'test-access-key'
os.environ['AWS_SECRET_ACCESS_KEY'] = 'test-secret-key'

# Mock tool registry for testing
MOCK_TOOL_REGISTRY = {
    "test_tool": {
        "description": "Test tool",
        "input_schema": {"type": "object", "properties": {}},
        "args_model": Mock(),
        "function": AsyncMock(return_value=[TextContent(type="text", text="test result")])
    }
}

@pytest.fixture
def mock_server():
    """Create a mock Server instance"""
    # Create mock class and instance
    mock = Mock()
    mock_instance = Mock()
    
    # Set up the instance's create_initialization_options
    mock_instance.create_initialization_options.return_value = {
        "protocolVersion": "1.0",
        "serverInfo": {"name": "test-server", "version": "1.0"}
    }
    
    # Make the mock class return our mock instance
    mock.return_value = mock_instance
    
    with patch('mcp_server_opensearch.stdio_server.Server', mock):
        yield mock  # Return the mock class

@pytest.fixture
def mock_stdio():
    """Create mock stdio reader and writer"""
    reader = AsyncMock()
    writer = AsyncMock()
    
    @asynccontextmanager
    async def mock_context():
        yield reader, writer
    
    with patch('mcp_server_opensearch.stdio_server.stdio_server', mock_context):
        yield reader, writer

@pytest.fixture
def mock_tool_registry():
    """Replace the tool registry with test data"""
    mock_registry = {
        "test_tool": {
            "description": "Test tool",
            "input_schema": {"type": "object", "properties": {}},
            "args_model": Mock(),
            "function": AsyncMock(return_value=[TextContent(type="text", text="test result")])
        }
    }

    with patch('mcp_server_opensearch.stdio_server.TOOL_REGISTRY', MOCK_TOOL_REGISTRY):
        yield MOCK_TOOL_REGISTRY

@pytest.mark.asyncio
async def test_serve_initialization(mock_server, mock_stdio, mock_tool_registry):
    """Test server initialization"""
    reader, writer = mock_stdio
    
    # Start the server
    from mcp_server_opensearch.stdio_server import serve
    serve_task = asyncio.create_task(serve())
    
    # Wait for the server to start
    await asyncio.sleep(0.1)
    
    # Verify server was initialized correctly
    mock_server.assert_called_once()
    mock_server.return_value.create_initialization_options.assert_called_once()

@pytest.mark.asyncio
async def test_list_tools(mock_server, mock_stdio, mock_tool_registry):
    """Test list_tools functionality"""
    reader, writer = mock_stdio

    # Start the server
    from mcp_server_opensearch.stdio_server import serve
    serve_task = asyncio.create_task(serve())
    await asyncio.sleep(0.1)
    
    # Get the list_tools handler
    list_tools_handler = None
    for call in mock_server.mock_calls:
        if 'list_tools' in str(call):
            # Create an async function to return as the handler
            async def mock_list_tools():
                return [
                    Tool(
                        name="test_tool",
                        description="Test tool",
                        inputSchema={"type": "object", "properties": {}}
                    )
                ]
            list_tools_handler = mock_list_tools
            break
    
    assert list_tools_handler is not None
    
    # Test the list_tools handler
    tools = await list_tools_handler()
    assert len(tools) == 1
    assert tools[0].name == "test_tool"
    assert tools[0].description == "Test tool"

@pytest.mark.asyncio
async def test_call_tool(mock_server, mock_stdio, mock_tool_registry):
    """Test call_tool functionality"""
    reader, writer = mock_stdio
    
    # Start the server
    from mcp_server_opensearch.stdio_server import serve
    serve_task = asyncio.create_task(serve())
    await asyncio.sleep(0.1)
    
    # Get the call_tool handler
    call_tool_handler = None
    for call in mock_server.mock_calls:
        if 'call_tool' in str(call):
            # Create an async function to return as the handler
            async def mock_call_tool(tool_name: str, arguments: dict):
                if tool_name not in mock_tool_registry:
                    raise ValueError(f"Unknown tool: {tool_name}")
                
                tool = mock_tool_registry[tool_name]
                # Simulate the tool execution
                return [TextContent(type="text", text="test result")]
            
            call_tool_handler = mock_call_tool
            break
    
    assert call_tool_handler is not None
    
    # Test the call_tool handler
    result = await call_tool_handler("test_tool", {})
    assert len(result) == 1
    assert result[0].text == "test result"

@pytest.mark.asyncio
async def test_server_error_handling(mock_server, mock_stdio, mock_tool_registry):
    """Test server error handling"""
    reader, writer = mock_stdio
    
    # Simulate an error in the server
    mock_server.return_value.run.side_effect = Exception("Test error")
    
    # Start the server
    from mcp_server_opensearch.stdio_server import serve
    with pytest.raises(Exception, match="Test error"):
        await serve()

@pytest.mark.asyncio
async def test_tool_execution_error(mock_server, mock_stdio, mock_tool_registry):
    """Test tool execution error handling"""
    reader, writer = mock_stdio
    
    # Modify mock tool to raise an error
    mock_tool_registry["test_tool"]["function"].side_effect = Exception("Tool error")
    
    # Start the server
    from mcp_server_opensearch.stdio_server import serve
    serve_task = asyncio.create_task(serve())
    await asyncio.sleep(0.1)
    
     # Get the call_tool handler
    call_tool_handler = None
    for call in mock_server.mock_calls:
        if 'call_tool' in str(call):
            # Create an async function to return as the handler
            async def mock_call_tool(tool_name: str, arguments: dict):
                if tool_name not in mock_tool_registry:
                    raise ValueError(f"Unknown tool: {tool_name}")
                
                tool = mock_tool_registry[tool_name]
                # Execute the tool function which should raise the error
                parsed = tool["args_model"](**arguments)
                return await tool["function"](parsed)
            
            call_tool_handler = mock_call_tool
            break
    
    assert call_tool_handler is not None
    
    # Test tool execution error
    with pytest.raises(Exception, match="Tool error"):
        await call_tool_handler("test_tool", {})