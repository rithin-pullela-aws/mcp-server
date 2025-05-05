# OpenSearch MCP Server
A minimal Model Context Protocol (MCP) server for OpenSearch exposing 4 tools over stdio and sse server.

## Available tools
- ListIndexTool: Lists all indices in OpenSearch.
- IndexMappingTool: Retrieves index mapping and setting information for an index in OpenSearch.
- SearchIndexTool: Searches an index using a query written in query domain-specific language (DSL) in OpenSearch.
- GetShardsTool: Gets information about shards in OpenSearch.

> More tools coming soon. [Click here](#contributing) to learn how to add new tools.

## Installation

Install from PyPI:
```
pip install test-opensearch-mcp
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

**Note**: These commands must be run from the `src` directory of the project.

- **Stdio Server**
```
uv run python -m mcp_server_opensearch 
```

- **SSE Server**
```
uv run python -m mcp_server_opensearch --transport sse
```

## Claude Desktop Integration
### Using the Published [PyPI Package](https://pypi.org/project/test-opensearch-mcp/)
```
{
    "mcpServers": {
        "opensearch-mcp-server": {
            "command": "uvx",
            "args": [
                "test-opensearch-mcp"
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

### Using the Installed Package (via pip):
```
{
    "mcpServers": {
        "opensearch-mcp-server": {
            "command": "python",  // Or full path to python with PyPI package installed
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

### Using Local Clone:
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

## Contributing {#contributing}
### Adding Custom Tools
To add a new tool to the MCP server, follow these steps:

1. Create a new tool function in `src/tools/tools.py`:
```python
async def your_tool_function(args: YourToolArgs) -> list[dict]:
    try:
        # Your tool implementation here
        result = your_implementation()
        return [{
            "type": "text",
            "text": result
        }]
    except Exception as e:
        return [{
            "type": "text",
            "text": f"Error: {str(e)}"
        }]
```

2. Define the arguments model using Pydantic:
```python
class YourToolArgs(BaseModel):
    # Define your tool's parameters here
    param1: str
    param2: int
```

3. Register your tool in the `TOOL_REGISTRY` dictionary:
```python
TOOL_REGISTRY = {
    # ... existing tools ...
    "YourToolName": {
        "description": "Description of what your tool does",
        "input_schema": YourToolArgs.model_json_schema(),
        "function": your_tool_function,
        "args_model": YourToolArgs,
    }
}
```

4. Add helper functions in `src/opensearch/helper.py`:
```python
def your_helper_function(param1: str, param2: int) -> dict:
    """
    Helper function that performs a single REST call to OpenSearch.
    Each helper should be focused on one specific OpenSearch operation.
    This promotes clarity and maintainable architecture.
    """
    # Your OpenSearch REST call implementation here
    return result
```

5. Import and use the helper functions in your tool:
```python
from opensearch.helper import your_helper_function
```

The tool will be automatically available through the MCP server after registration.

> Note: Each helper function should perform a single REST call to OpenSearch. This design promotes:
> - Clear separation of concerns
> - Easy testing and maintenance
> - Extensible architecture
> - Reusable OpenSearch operations