### OpenSearch MCP Server (stdio)
A minimal Model Context Protocol (MCP) server for OpenSearch exposing 4 tools over stdio and sse server.

## Installation:

This can be installed from PyPI via pip:
```
pip install test-mcp-opensearch
```

### Environment Variables

Configure authentication by setting the appropriate environment variables:

**Basic Authentication**
```
export OPENSEARCH_URL="<your_opensearch_domain_url>"
export OPENSEARCH_USERNAME="<your_opensearch_domain_username>"
export OPENSEARCH_PASSWORD="<your_opensearch_domain_password>"
```

**IAM Role Authentication**
```
export OPENSEARCH_URL="<your_opensearch_domain_url>"
export AWS_REGION="<your_aws_region>"
export AWS_ACCESS_KEY="<your_aws_access_key>"
export AWS_SECRET_ACCESS_KEY="<your_aws_secret_access_key>"
export AWS_SESSION_TOKEN="<your_aws_session_token>"
```

### Running the Server

**Stdio Server**
```
python -m mcp_server_opensearch
```

**SSE Server**
```
python -m mcp_server_opensearch --transport sse
```

## Development Setup:

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

### Running the Stdio Server
```
uv run python -m mcp_server_opensearch 
```

### Running the SSE Server
```
uv run python -m mcp_server_opensearch --transport sse
```

## Available tools
- list_indices: Lists all indices in OpenSearch.
- get_index_mapping: Gets the mapping for specified index.
- search_index: Searches an index using a query.
- get_shards: Gets information about shards in OpenSearch cluster.

> More tools coming soon

## Integration with Claude Desktop
### Using basic authentication:
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
                "OPENSEARCH_URL": "<your_opensearch_domain_url>",
                "OPENSEARCH_USERNAME": "<your_opensearch_domain_username>",
                "OPENSEARCH_PASSWORD": "<your_opensearch_domain_password>"
            }
        }
    }
}

```

### Using IAM Role authentication:
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
                "OPENSEARCH_URL": "<your_opensearch_domain_url>",
                "AWS_REGION": "<your_aws_region>",
                "AWS_ACCESS_KEY": "<your_aws_access_key>",
                "AWS_SECRET_ACCESS_KEY": "<your_aws_secret_access_key>",
                "AWS_SESSION_TOKEN": "<your_aws_session_token>",
            }
        }
    }
}
```