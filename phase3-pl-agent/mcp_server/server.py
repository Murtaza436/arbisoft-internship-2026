import os
import json
from mcp.server import Server
from mcp.server.stdio import stdio_server
from mcp import types
from src.tools.live_tool import get_standings, get_top_scorers

app = Server('pl-research-server')


@app.list_resources()
async def list_resources() -> list[types.Resource]:
    return [
        types.Resource(
            uri='pl://standings',
            name='Premier League Standings',
            description='Current Premier League table and standings',
            mimeType='text/plain',
        ),
        types.Resource(
            uri='pl://scorers',
            name='Top Scorers',
            description='Current Premier League top scorers',
            mimeType='text/plain',
        ),
    ]


@app.read_resource()
async def read_resource(uri: str) -> str:
    if uri == 'pl://standings':
        return get_standings()
    if uri == 'pl://scorers':
        return get_top_scorers()
    raise ValueError(f'Unknown resource: {uri}')


@app.list_tools()
async def list_tools() -> list[types.Tool]:
    return [
        types.Tool(
            name='get_pl_standings',
            description='Get current Premier League standings',
            inputSchema={
                'type': 'object',
                'properties': {},
                'required': [],
            },
        ),
        types.Tool(
            name='get_pl_scorers',
            description='Get current Premier League top scorers',
            inputSchema={
                'type': 'object',
                'properties': {},
                'required': [],
            },
        ),
    ]


@app.call_tool()
async def call_tool(
    name: str,
    arguments: dict,
) -> list[types.TextContent]:
    if name == 'get_pl_standings':
        result = get_standings()
        return [types.TextContent(type='text', text=result)]
    if name == 'get_pl_scorers':
        result = get_top_scorers()
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
