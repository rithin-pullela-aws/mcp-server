# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import argparse
from typing import Any

import uvicorn
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import JSONResponse
from starlette.routing import Mount, Route
from starlette.middleware import Middleware
from starlette.middleware.base import BaseHTTPMiddleware
from mcp.server.sse import SseServerTransport
from mcp.server import Server
from mcp.types import TextContent, Tool
from tools.tools import TOOL_REGISTRY

# Constants
API_KEY = "secret-token"

class APIKeyMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        auth_header = request.headers.get("authorization")
        if not auth_header or auth_header != f"Bearer {API_KEY}":
            return JSONResponse({"detail": "Unauthorized"}, status_code=401)
        return await call_next(request)

def create_mcp_server() -> Server:
    server = Server("opensearch-mcp-server")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        tools = []
        for tool_name, tool_info in TOOL_REGISTRY.items():
            tools.append(Tool(
                name=tool_name,
                description=tool_info["description"],
                inputSchema=tool_info["input_schema"]
            ))
        return tools

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        tool = TOOL_REGISTRY[name]
        if not tool:
            raise ValueError(f"Unknown tool: {name}")
        parsed = tool["args_model"](**arguments)
        return await tool["function"](parsed)

    return server

class MCPStarletteApp:
    def __init__(self, mcp_server: Server):
        self.mcp_server = mcp_server
        self.sse = SseServerTransport("/messages/")

    async def handle_sse(self, request: Request) -> None:
        async with self.sse.connect_sse(
                request.scope,
                request.receive,
                request._send,
        ) as (read_stream, write_stream):
            await self.mcp_server.run(
                read_stream,
                write_stream,
                self.mcp_server.create_initialization_options(),
            )

    def create_app(self) -> Starlette:
        return Starlette(
            routes=[
                Route("/sse", endpoint=self.handle_sse, methods=["POST"]),
                Mount("/messages/", app=self.sse.handle_post_message),
            ],
            middleware=[Middleware(APIKeyMiddleware)],
        )

async def serve(host: str = "0.0.0.0", port: int = 9900) -> None:
    mcp_server = create_mcp_server()
    app_handler = MCPStarletteApp(mcp_server)
    app = app_handler.create_app()
    
    config = uvicorn.Config(
        app=app,
        host=host,
        port=port,
    )
    server = uvicorn.Server(config)
    await server.serve()

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description='Run OpenSearch MCP SSE-based server')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=9900, help='Port to listen on')
    args = parser.parse_args()

    import asyncio
    asyncio.run(serve(host=args.host, port=args.port))