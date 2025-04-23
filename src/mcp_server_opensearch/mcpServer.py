# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import logging
from enum import Enum

from pydantic import BaseModel
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from tools.tools import TOOL_REGISTRY

# --- Server setup ---
async def serve() -> None:
    logger = logging.getLogger(__name__)
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

    # Start stdio-based MCP server
    options = server.create_initialization_options()
    async with stdio_server() as (reader, writer):
        await server.run(reader, writer, options, raise_exceptions=True)

def main() -> None:
    import anyio
    anyio.run(serve)

if __name__ == "__main__":
    main()
