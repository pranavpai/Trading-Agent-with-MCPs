import mcp
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters
from agents import FunctionTool
import json

# Set up server parameters to launch accounts_server.py via uv
params = StdioServerParameters(command="uv", args=["run", "accounts_server.py"], env=None)


async def list_accounts_tools():
    async with stdio_client(params) as streams:  # Create stdio connection to MCP server
        async with mcp.ClientSession(*streams) as session:  # Initialize client session
            await session.initialize()  # Complete MCP handshake
            tools_result = await session.list_tools()  # Get available tools from server
            return tools_result.tools
        
async def call_accounts_tool(tool_name, tool_args):
    async with stdio_client(params) as streams:  # Create stdio connection to MCP server
        async with mcp.ClientSession(*streams) as session:  # Initialize client session
            await session.initialize()  # Complete MCP handshake
            result = await session.call_tool(tool_name, tool_args)  # Execute tool with arguments
            return result
            
async def read_accounts_resource(name):
    async with stdio_client(params) as streams:  # Create stdio connection to MCP server
        async with mcp.ClientSession(*streams) as session:  # Initialize client session
            await session.initialize()  # Complete MCP handshake
            result = await session.read_resource(f"accounts://accounts_server/{name}")  # Read resource by URI
            return result.contents[0].text  # Extract text content from resource
        
async def read_strategy_resource(name):
    async with stdio_client(params) as streams:  # Create stdio connection to MCP server
        async with mcp.ClientSession(*streams) as session:  # Initialize client session
            await session.initialize()  # Complete MCP handshake
            result = await session.read_resource(f"accounts://strategy/{name}")  # Read strategy resource by URI
            return result.contents[0].text  # Extract text content from resource

async def get_accounts_tools_openai(): # This function converts MCP tools to OpenAI-compatible tools
    openai_tools = [] # This list will store the OpenAI-compatible tools
    for tool in await list_accounts_tools():  # Get all available MCP tools
        schema = {**tool.inputSchema, "additionalProperties": False}  # Convert MCP schema to OpenAI format
        openai_tool = FunctionTool(  # Create OpenAI-compatible tool wrapper
            name=tool.name,
            description=tool.description,
            params_json_schema=schema,
            on_invoke_tool=lambda ctx, args, toolname=tool.name: call_accounts_tool(toolname, json.loads(args))  # This is the function that will be called when the tool is invoked
                
        )
        openai_tools.append(openai_tool)
    return openai_tools  # Return list of OpenAI-compatible tools