import asyncio
import json
from mcp import ClientSession
from mcp.client.stdio import stdio_client
from mcp import types
from src.tracer import trace


async def call_mcp_tool(tool_name: str, arguments: dict) -> str:
    server_params = types.StdioServerParameters(
        command='python',
        args=['-m', 'mcp_server.server'],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            trace('mcp_client', 'tool_call', {
                'tool': tool_name,
                'args': arguments,
            })
            result = await session.call_tool(tool_name, arguments)
            content = result.content[0].text if result.content else ''
            trace('mcp_client', 'tool_result', {
                'tool': tool_name,
                'preview': content[:200],
            })
            return content


async def read_mcp_resource(uri: str) -> str:
    server_params = types.StdioServerParameters(
        command='python',
        args=['-m', 'mcp_server.server'],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            trace('mcp_client', 'resource_read', {'uri': uri})
            result = await session.read_resource(uri)
            return result.contents[0].text if result.contents else ''


def run_mcp_tool(tool_name: str, arguments: dict) -> str:
    return asyncio.run(call_mcp_tool(tool_name, arguments))


def run_mcp_resource(uri: str) -> str:
    return asyncio.run(read_mcp_resource(uri))
