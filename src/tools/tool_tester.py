import asyncio
from tools.tools import list_indices_tool  # use absolute import

async def main():
    tools = await list_indices_tool(None)
    print(tools)

if __name__ == "__main__":
    asyncio.run(main())