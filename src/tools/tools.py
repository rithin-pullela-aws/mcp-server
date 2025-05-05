# Copyright OpenSearch Contributors
# SPDX-License-Identifier: Apache-2.0

from pydantic import BaseModel
from mcp.types import TextContent
from opensearch.helper import list_indices, get_index_mapping, search_index, get_shards
from typing import Any
import json

class ListIndicesArgs(BaseModel):
    pass  # no args needed

class GetIndexMappingArgs(BaseModel):
    index: str

class SearchIndexArgs(BaseModel):
    index: str
    query: Any

class GetShardsArgs(BaseModel):
    index: str

async def list_indices_tool(args: ListIndicesArgs) -> list[dict]:
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

async def get_index_mapping_tool(args: GetIndexMappingArgs) -> list[dict]:
    try:
        mapping = get_index_mapping(args.index)
        formatted_mapping = json.dumps(mapping, indent=2)
        
        return [{
            "type": "text",
            "text": f"Mapping for {args.index}:\n{formatted_mapping}"
        }]
    except Exception as e:
        return [{
            "type": "text",
            "text": f"Error getting mapping: {str(e)}"
        }]

async def search_index_tool(args: SearchIndexArgs) -> list[dict]:
    try:
        result = search_index(args.index, args.query)
        formatted_result = json.dumps(result, indent=2)
        
        return [{
            "type": "text",
            "text": f"Search results from {args.index}:\n{formatted_result}"
        }]
    except Exception as e:
        return [{
            "type": "text",
            "text": f"Error searching index: {str(e)}"
        }]

async def get_shards_tool(args: GetShardsArgs) -> list[dict]:
    try:
        result = get_shards(args.index)
        
        if isinstance(result, dict) and "error" in result:
            return [{
                "type": "text",
                "text": f"Error getting shards: {result['error']}"
            }]
        formatted_text = "index | shard | prirep | state | docs | store | ip | node\n"
        
        # Format each shard row
        for shard in result:
            formatted_text += f"{shard['index']} | "
            formatted_text += f"{shard['shard']} | "
            formatted_text += f"{shard['prirep']} | "
            formatted_text += f"{shard['state']} | "
            formatted_text += f"{shard['docs']} | "
            formatted_text += f"{shard['store']} | "
            formatted_text += f"{shard['ip']} | "
            formatted_text += f"{shard['node']}\n"

        return [{
            "type": "text",
            "text": formatted_text
        }]
    except Exception as e:
        return [{
            "type": "text",
            "text": f"Error getting shards information: {str(e)}"
        }]

TOOL_REGISTRY = {
    "list_indices": {
        "description": "Lists all indices in OpenSearch",
        "input_schema": ListIndicesArgs.model_json_schema(),
        "function": list_indices_tool,
        "args_model": ListIndicesArgs,
    },
    "get_index_mapping": {
        "description": "Gets the mapping for specified index",
        "input_schema": GetIndexMappingArgs.model_json_schema(),
        "function": get_index_mapping_tool,
        "args_model": GetIndexMappingArgs,
    },
    "search_index": {
        "description": "Searches an index using a query",
        "input_schema": SearchIndexArgs.model_json_schema(),
        "function": search_index_tool,
        "args_model": SearchIndexArgs,
    },
    "get_shards": {
        "description": "Gets information about shards in OpenSearch cluster",
        "input_schema": GetShardsArgs.model_json_schema(),
        "function": get_shards_tool,
        "args_model": GetShardsArgs,
    }
}