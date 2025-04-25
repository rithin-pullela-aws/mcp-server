from pydantic import BaseModel
from mcp.types import TextContent
from opensearch.helper import list_indices
import json

class ListIndicesArgs(BaseModel):
    pass  # no args needed

async def list_indices_tool(args: ListIndicesArgs) -> list[TextContent]:
    try:
        indices = list_indices()
        indices_text = "\n".join(index['index'] for index in indices)
        
        # Return in MCP expected format
        return [{
            "type": "text",
            "text": indices_text
        }]
    except Exception as e:
        return [{
            "type": "text",
            "text": f"Error listing indices: {str(e)}"
        }]

TOOL_REGISTRY = {
    "list_indices": {
        "description": "List all indices in OpenSearch",
        "input_schema": ListIndicesArgs.model_json_schema(),
        "function": list_indices_tool,
        "args_model": ListIndicesArgs,
    }
}