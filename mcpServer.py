# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

import logging
import os
import json
from enum import Enum

from pydantic import BaseModel
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp.types import TextContent, Tool
from opensearchpy import OpenSearch
from opensearchpy.exceptions import OpenSearchException

# --- Argument models ---
class ListIndicesArgs(BaseModel):
    # No fields needed for listing indices
    pass

# --- Tool names ---
class MCPTools(str, Enum):
    LIST_INDICES = "list_indices"

# --- OpenSearch client factory ---
def make_client() -> OpenSearch:
    url      = os.getenv("OPENSEARCH_URL", "http://localhost:9200")
    user     = os.getenv("OPENSEARCH_USERNAME")
    password = os.getenv("OPENSEARCH_PASSWORD")
    return OpenSearch(url, http_auth=(user, password))

# --- Tool implementation ---
async def list_indices_tool(args: ListIndicesArgs) -> list[TextContent]:
    client = make_client()
    try:
        indices = client.cat.indices(format="json")
        return [
            TextContent(
                type="application/json",
                text=json.dumps(indices)
            )
        ]
    except OpenSearchException as e:
        return [
            TextContent(
                type="text",
                text=f"Error fetching indices: {e}"
            )
        ]
    except Exception as e:
        return [
            TextContent(
                type="text",
                text=f"Unexpected error: {e}"
            )
        ]

# --- Server setup ---
async def serve() -> None:
    logger = logging.getLogger(__name__)
    server = Server("opensearch-mcp-server")

    @server.list_tools()
    async def list_tools() -> list[Tool]:
        return [
            Tool(
                name=MCPTools.LIST_INDICES,
                description="List all OpenSearch indices via the cat.indices API",
                inputSchema=ListIndicesArgs.schema(),
            )
        ]

    @server.call_tool()
    async def call_tool(name: str, arguments: dict) -> list[TextContent]:
        match name:
            case MCPTools.LIST_INDICES:
                args = ListIndicesArgs(**arguments)
                return await list_indices_tool(args)

            case _:
                raise ValueError(f"Unknown tool: {name}")

    # Start stdio-based MCP server
    options = server.create_initialization_options()
    async with stdio_server() as (reader, writer):
        await server.run(reader, writer, options, raise_exceptions=True)

def main() -> None:
    import anyio
    anyio.run(serve)

if __name__ == "__main__":
    main()
