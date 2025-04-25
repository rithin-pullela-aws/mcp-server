### OpenSearch MCP Server (stdio)
A minimal Model Context Protocol (MCP) server for OpenSearch exposing a single list_indices tool over stdio.

## Development Notes:

1. Create & activate a virtual environment
```
uv venv 
source .venv/bin/activate
```

2. Install dependencies

```
uv sync # to install dependencies from uv.lock
```

To manually add new dependencies:
```
uv add <package-name>
```

Note, this adds updates the pyproject.toml, uv.lock, and installs in virtual environment

3. Manual updates

If you modify pyproject.toml manually:

```
uv lock 
uv sync
```

## Running the Stdio Server
```
uv run python -m mcp_server_opensearch 
```

## Running the SSE Server
```
uv run python -m mcp_server_opensearch --transport sse
```

## Available tool
- list_indices: Lists all indices in OpenSearch.
- get_index_mapping: Gets the mapping for specified index.
- search_index: Searches an index using a query.
- get_shards: Gets information about shards in OpenSearch cluster.

> More tools coming soon

### To add the Local clone to Claude desktop:
```
{
    "mcpServers": {
        "opensearch-mcp-server": {
        "command": "/opt/homebrew/bin/uv", #I mentioned path to uv, ideally uv is enough
        "args": [
            "--directory",
            "path/to/the/clone/mcp-server",
            "run",
            "--",
            "python",
            "-m",
            "mcp_server_opensearch"
        ],
        "env": {
            
        }
        }
    }
}

```
