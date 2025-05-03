from opensearchpy import OpenSearch
from .client import client
import json
from typing import Any

# List all the helper functions, these functions perform a single rest call to opensearch
# these functions will be used in tools folder to eventually write more complex tools
def list_indices() -> json:
    response = client.cat.indices(format="json")
    return response

def get_index_mapping(index: str) -> json:
    response = client.indices.get_mapping(index=index)
    return response

def search_index(index: str, query: Any) -> json:
    response = client.search(index=index, body=query)
    return response

def get_shards(index: str) -> json:
    response = client.cat.shards(index=index, format="json")
    return response