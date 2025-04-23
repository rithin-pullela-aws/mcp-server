from .mcpServer import serve

def main() -> None:
    import asyncio
    asyncio.run(serve())
