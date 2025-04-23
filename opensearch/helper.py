from opensearchpy import OpenSearch
from .client import client
import json

# List all the helper functions, these functions perfrom a single rest call to opensearch
# these functions will be used in tools folder to eventually write more complex tools
def list_indices() -> json:
    response = client.cat.indices(format="json")
    return response
