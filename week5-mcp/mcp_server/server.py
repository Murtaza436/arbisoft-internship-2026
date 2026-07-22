import os
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from src.tools import web_search

app = Server('week5-research-server')


@app.list_resources()
async def list_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri='file://files/knowledge.txt',
            name='Knowledge Base',
            description='Local knowledge base text file',
            mimeType='text/plain',
        )
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    if uri == 'file://files/knowledge.txt':
        path = 'files/knowledge.txt'
        if os.path.exists(path):
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return 'Knowledge base file not found.'
    raise ValueError(f'Unknown resource: {uri}')


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name='web_search',
            description='Search the web for current information.',
            inputSchema={
                'type': 'object',
                'properties': {
                    'query': {
                        'type': 'string',
                        'description': 'The search query.',
                    }
                },
                'required': ['query'],
            },
        )
    ]


@app.call_tool()
async def call_tool(
    name: str,
    arguments: dict,
) -> list[types.TextContent]:
    if name == 'web_search':
        query = arguments.get('query', '')
        result = web_search(query)
        return [types.TextContent(type='text', text=result)]
    raise ValueError(f'Unknown tool: {name}')


async def main():
    async with stdio_server() as (read_stream, write_stream):
        await app.run(
            read_stream,
            write_stream,
            app.create_initialization_options(),
        )


if __name__ == '__main__':
    import asyncio
    asyncio.run(main())
