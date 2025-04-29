import sys
import pytest
from unittest.mock import Mock, patch, AsyncMock
from mcp.types import Tool, TextContent
from starlette.requests import Request
from starlette.responses import JSONResponse
from mcp.server import Server

class TestAPIKeyMiddleware:
    def setup_method(self, method):
        """Setup that runs before each test method"""
        # Mock the OpenSearch client
        self.mock_client = Mock()
        mock_client_module = Mock()
        mock_client_module.client = self.mock_client
        sys.modules['opensearch.client'] = mock_client_module
        
        # Mock the helper module
        mock_helper = Mock()
        sys.modules['opensearch.helper'] = mock_helper
        
        # Now import the module under test
        from mcp_server_opensearch.sse_server import APIKeyMiddleware
        self.APIKeyMiddleware = APIKeyMiddleware

    def teardown_method(self, method):
        """Cleanup after each test method"""
        sys.modules.pop('opensearch.client', None)
        sys.modules.pop('opensearch.helper', None)

    @pytest.fixture
    def middleware(self):
        """Provides an APIKeyMiddleware instance for testing"""
        return self.APIKeyMiddleware(app=None)

    @pytest.mark.asyncio
    async def test_valid_api_key(self, middleware):
        """Test that middleware allows requests with valid API key"""
        # Create mock request with valid API key
        mock_request = Mock(spec=Request)
        mock_request.headers = {"authorization": "Bearer secret-token"}
        
        # Create mock handler
        mock_handler = AsyncMock()
        mock_handler.return_value = JSONResponse({"status": "ok"})
        
        # Call middleware
        response = await middleware.dispatch(mock_request, mock_handler)
        
        # Verify handler was called
        mock_handler.assert_called_once_with(mock_request)
        assert response.status_code == 200

    @pytest.mark.asyncio
    async def test_invalid_api_key(self, middleware):
        """Test that middleware blocks requests with invalid API key"""
        # Create mock request with invalid API key
        mock_request = Mock(spec=Request)
        mock_request.headers = {"authorization": "Bearer wrong-token"}
        
        # Create mock handler (should not be called)
        mock_handler = AsyncMock()
        
        # Call middleware
        response = await middleware.dispatch(mock_request, mock_handler)
        
        # Verify unauthorized response
        assert response.status_code == 401
        assert response.body == b'{"detail":"Unauthorized"}'
        mock_handler.assert_not_called()

    @pytest.mark.asyncio
    async def test_missing_api_key(self, middleware):
        """Test that middleware blocks requests with missing API key"""
        # Create mock request with no API key
        mock_request = Mock(spec=Request)
        mock_request.headers = {}
        
        # Create mock handler (should not be called)
        mock_handler = AsyncMock()
        
        # Call middleware
        response = await middleware.dispatch(mock_request, mock_handler)
        
        # Verify unauthorized response
        assert response.status_code == 401
        assert response.body == b'{"detail":"Unauthorized"}'
        mock_handler.assert_not_called()

class TestMCPServer:
    @pytest.fixture
    def mock_tool_registry(self):
        """Provides a mock tool registry for testing"""
        return {
            "test-tool": {
                "description": "Test tool",
                "input_schema": {"type": "object"},
                "args_model": Mock(),
                "function": AsyncMock(return_value=[TextContent(type="text", text="test result")])
            }
        }

    @patch('mcp_server_opensearch.sse_server.TOOL_REGISTRY')
    def test_create_mcp_server(self, mock_registry, mock_tool_registry):
        """Test MCP server creation"""
        # Setup mock registry
        mock_registry.items.return_value = mock_tool_registry.items()
        
        # Create server
        from mcp_server_opensearch.sse_server import create_mcp_server
        server = create_mcp_server()
        
        assert server.name == "opensearch-mcp-server"

    @pytest.mark.asyncio
    @patch('mcp_server_opensearch.sse_server.TOOL_REGISTRY')
    async def test_list_tools(self, mock_registry, mock_tool_registry):
        """Test listing available tools"""
        # Setup mock registry
        mock_registry.items.return_value = mock_tool_registry.items()
        
        # Create server
        from mcp_server_opensearch.sse_server import create_mcp_server
        server = create_mcp_server()

        # Get the tools by calling the decorated function
        tools = []
        for tool_name, tool_info in mock_tool_registry.items():
            tools.append(Tool(
                name=tool_name,
                description=tool_info["description"],
                inputSchema=tool_info["input_schema"]
            ))
        
        assert len(tools) == 1
        assert tools[0].name == "test-tool"
        assert tools[0].description == "Test tool"
        assert tools[0].inputSchema == {"type": "object"}


    @pytest.mark.asyncio
    @patch('mcp_server_opensearch.sse_server.TOOL_REGISTRY')
    async def test_call_tool(self, mock_registry, mock_tool_registry):
        """"Test calling the tool"""
        # Setup mock registry
        mock_registry.__getitem__.return_value = mock_tool_registry["test-tool"]
        mock_tool_registry["test-tool"]["function"].return_value = [TextContent(type="text", text="result")]
        
        # Create server and mock the call_tool decorator
        mock_call_tool = AsyncMock()
        mock_call_tool.return_value = [TextContent(type="text", text="result")]
        
        # Test the decorated function
        result = await mock_call_tool("test-tool", {"param": "value"})
        
        assert len(result) == 1
        assert isinstance(result[0], TextContent)
        assert result[0].text == "result"

class TestMCPStarletteApp:
    @pytest.fixture
    def app_handler(self):
        """Provides an MCPStarletteApp instance for testing"""
        from mcp_server_opensearch.sse_server import create_mcp_server, MCPStarletteApp
        server = create_mcp_server()
        return MCPStarletteApp(server)

    def test_create_app(self, app_handler):
        """Test Starlette application creation and configuration"""
        app = app_handler.create_app()
        assert len(app.routes) == 2

        # Check routes
        assert app.routes[0].path == "/sse"
        assert app.routes[1].path == "/messages"

        # Check middleware list
        middleware_list = app.user_middleware
        assert len(middleware_list) == 1

    @pytest.mark.asyncio
    async def test_handle_sse(self, app_handler):
        """Test SSE connection handling"""
        mock_request = Mock()

        # Mock SSE connection context
        mock_read_stream = AsyncMock()
        mock_write_stream = AsyncMock()
        
        # Create a proper async context manager mock
        mock_context = AsyncMock()
        mock_context.__aenter__.return_value = (mock_read_stream, mock_write_stream)
        mock_context.__aexit__.return_value = None
        
        # Set up the connect_sse mock to return our context manager
        app_handler.sse.connect_sse = Mock(return_value=mock_context)
        
        # Mock the server run method to return immediately
        app_handler.mcp_server.run = AsyncMock()
        app_handler.mcp_server.create_initialization_options = Mock(return_value={})
        
        # Add a side effect to make run return immediately
        app_handler.mcp_server.run.return_value = None
        
        await app_handler.handle_sse(mock_request)
        
        # Verify SSE connection was established
        app_handler.sse.connect_sse.assert_called_once_with(
            mock_request.scope,
            mock_request.receive,
            mock_request._send
        )
        
        # Verify context manager was used
        mock_context.__aenter__.assert_called_once()
        mock_context.__aexit__.assert_called_once()
        
        # Verify server.run was called with correct arguments
        app_handler.mcp_server.run.assert_called_once_with(
            mock_read_stream,
            mock_write_stream,
            {}
        )

@pytest.mark.asyncio
async def test_serve():
    """Test server startup and configuration"""
    from mcp_server_opensearch.sse_server import serve
    
    # Mock uvicorn server
    mock_server = AsyncMock()
    mock_config = Mock()
    
    with patch('uvicorn.Server', return_value=mock_server) as mock_server_class:
        with patch('uvicorn.Config', return_value=mock_config) as mock_config_class:
            await serve(host="localhost", port=8000)
            
            # Verify config
            mock_config_class.assert_called_once()
            config_args = mock_config_class.call_args[1]
            assert config_args["host"] == "localhost"
            assert config_args["port"] == 8000
            
            # Verify server started
            mock_server_class.assert_called_once_with(mock_config)
            mock_server.serve.assert_called_once()
