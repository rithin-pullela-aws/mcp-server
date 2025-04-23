from .mcpServer import serve

def main() -> None:
    import asyncio
    asyncio.run(serve())

if __name__ == "__main__":
    main()