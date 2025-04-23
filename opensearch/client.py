from opensearchpy import OpenSearch
import os

# This file should expose the OpenSearch py client

# TODO: Write better code similar to Nathalie's code for opensearch cli 
def make_client() -> OpenSearch:
    url      = os.getenv("OPENSEARCH_URL", "http://localhost:9200")
    user     = os.getenv("OPENSEARCH_USERNAME", "admin")
    password = os.getenv("OPENSEARCH_PASSWORD", "MyPassword123!")
    return OpenSearch(url, http_auth=(user, password))

client = make_client()