# Developer Guide
## Local Development Setup
1. Clone the Repository
```
git clone git@github.com:rithin-pullela-aws/opensearch-mcp-server.git

cd opensearch-mcp-server
```

2. Set Up Development Environment
```
# Create & activate a virtual environment
uv venv 
source .venv/bin/activate

# Install dependencies
uv sync
```

3. Running the Server Locally

**Important**: These commands must be run from the src directory
```
cd src

# Run stdio server
uv run python -m mcp_server_opensearch 

# Run SSE server
uv run python -m mcp_server_opensearch --transport sse
```

### Managing Dependencies
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

## Claude Desktop Integration (Development)
```
{
    "mcpServers": {
        "opensearch-mcp-server": {
            "command": "uv", # Or full path to uv
            "args": [
                "--directory",
                "path/to/the/clone/opensearch-mcp-server",
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

# Contributing
## Adding Custom Tools
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
