from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters
from src.tracer import trace


async def call_mcp_tool(tool_name: str, arguments: dict) -> str:
    server_params = StdioServerParameters(
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
    server_params = StdioServerParameters(
        command='python',
        args=['-m', 'mcp_server.server'],
    )
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            trace('mcp_client', 'resource_read', {'uri': uri})
            result = await session.read_resource(uri)
            return result.contents[0].text if result.contents else ''


async def run_mcp_tool(tool_name: str, arguments: dict) -> str:
    return await call_mcp_tool(tool_name, arguments)


async def run_mcp_resource(uri: str) -> str:
    return await read_mcp_resource(uri)
