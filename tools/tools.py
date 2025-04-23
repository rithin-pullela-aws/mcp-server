from pydantic import BaseModel
from mcp.types import TextContent
from opensearch.helper import list_indices
import json

class ListIndicesArgs(BaseModel):
    pass  # no args needed

async def list_indices_tool(args: ListIndicesArgs) -> list[TextContent]:
    indices = list_indices()
    return [index['index'] for index in indices]

TOOL_REGISTRY = {
    "list_indices": {
        "description": "List all indices in OpenSearch",
        "input_schema": ListIndicesArgs.model_json_schema(),
        "function": list_indices_tool,
        "args_model": ListIndicesArgs,
    }
}