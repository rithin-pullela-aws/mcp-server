# src/mcp_server_opensearch/__init__.py
from .stdio_server import serve as serve_stdio
from .sse_server import serve as serve_sse

def main() -> None:
    import argparse
    import asyncio

    parser = argparse.ArgumentParser(description='OpenSearch MCP Server')
    parser.add_argument(
        '--transport', 
        choices=['stdio', 'sse'], 
        default='stdio',
        help='Transport type (stdio or sse)'
    )
    parser.add_argument(
        '--host', 
        default='0.0.0.0', 
        help='Host to bind to (SSE only)'
    )
    parser.add_argument(
        '--port', 
        type=int, 
        default=9900, 
        help='Port to listen on (SSE only)'
    )

    args = parser.parse_args()

    if args.transport == 'stdio':
        asyncio.run(serve_stdio())
    else:
        asyncio.run(
            serve_sse(
                host=args.host,
                port=args.port
            )
        )

if __name__ == "__main__":
    main()