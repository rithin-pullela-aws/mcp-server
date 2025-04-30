# OpenSearch MCP Server
A minimal Model Context Protocol (MCP) server for OpenSearch exposing 4 tools over stdio and sse server.

## Available tools
- list_indices: Lists all indices in OpenSearch.
- get_index_mapping: Gets the mapping for specified index.
- search_index: Searches an index using a query.
- get_shards: Gets information about shards in OpenSearch cluster.

> More tools coming soon

## Installation

Install from PyPI:
```
pip install test-mcp-opensearch
```

## Configuration
### Authentication Methods:
- **Basic Authentication**
```
export OPENSEARCH_URL="<your_opensearch_domain_url>"
export OPENSEARCH_USERNAME="<your_opensearch_domain_username>"
export OPENSEARCH_PASSWORD="<your_opensearch_domain_password>"
```

- **IAM Role Authentication**
```
export OPENSEARCH_URL="<your_opensearch_domain_url>"
export AWS_REGION="<your_aws_region>"
export AWS_ACCESS_KEY="<your_aws_access_key>"
export AWS_SECRET_ACCESS_KEY="<your_aws_secret_access_key>"
export AWS_SESSION_TOKEN="<your_aws_session_token>"
```

## Usage
### Running with Python:

- **Stdio Server**
```
python -m mcp_server_opensearch
```

- **SSE Server**
```
python -m mcp_server_opensearch --transport sse
```

### Running with UV:

- **Stdio Server**
```
uv run python -m mcp_server_opensearch 
```

- **SSE Server**
```
uv run python -m mcp_server_opensearch --transport sse
```

## Development
### Environment Setup:

1. Create & activate a virtual environment
```
uv venv 
source .venv/bin/activate
```

2. Install dependencies

```
uv sync # Install from uv.lock
```

### Managing Dependencies:
- Add new dependencies:
```
uv add <package-name>
```

> Note: This automatically updates the pyproject.toml, uv.lock, and installs in virtual environment

- Update after manual pyproject.toml changes:
```
uv lock 
uv sync
```

## Claude Desktop Integration
### For Development (Using Local Clone):
```
{
    "mcpServers": {
        "opensearch-mcp-server": {
            "command": "uv", # Or full path to uv
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
                // Required
                "OPENSEARCH_URL": "<your_opensearch_domain_url>",

                // For Basic Authentication
                "OPENSEARCH_USERNAME": "<your_opensearch_domain_username>",
                "OPENSEARCH_PASSWORD": "<your_opensearch_domain_password>",

                // For IAM Role Authentication
                "AWS_REGION": "<your_aws_region>",
                "AWS_ACCESS_KEY": "<your_aws_access_key>",
                "AWS_SECRET_ACCESS_KEY": "<your_aws_secret_access_key>",
                "AWS_SESSION_TOKEN": "<your_aws_session_token>"
            }
        }
    }
}

```

### For Installed Package (Via pip):
```
{
    "mcpServers": {
        "opensearch-mcp-server": {
            "command": "python",  // Or full path to python
            "args": [
                "-m",
                "mcp_server_opensearch"
            ],
            "env": {
                // Required
                "OPENSEARCH_URL": "<your_opensearch_domain_url>",

                // For Basic Authentication
                "OPENSEARCH_USERNAME": "<your_opensearch_domain_username>",
                "OPENSEARCH_PASSWORD": "<your_opensearch_domain_password>",

                // For IAM Role Authentication
                "AWS_REGION": "<your_aws_region>",
                "AWS_ACCESS_KEY": "<your_aws_access_key>",
                "AWS_SECRET_ACCESS_KEY": "<your_aws_secret_access_key>",
                "AWS_SESSION_TOKEN": "<your_aws_session_token>"
            }
        }
    }
}
```