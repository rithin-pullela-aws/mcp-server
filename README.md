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

## Running the Server
```
uv run python -m mcp_server_opensearch 
```

## Available tool
- list_indices: Lists all indices in OpenSearch.

> More tools coming soon