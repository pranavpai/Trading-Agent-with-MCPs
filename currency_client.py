import mcp
from mcp.client.stdio import stdio_client
from mcp import StdioServerParameters
from agents import FunctionTool
import json

# Set up server parameters to launch currency_server.py via uv
params = StdioServerParameters(command="uv", args=["run", "currency_server.py"], env=None)

async def list_currency_tools():
    """List all available currency tools from the MCP server."""
    async with stdio_client(params) as streams:  # Create stdio connection to MCP server
        async with mcp.ClientSession(*streams) as session:  # Initialize client session
            await session.initialize()  # Complete MCP handshake
            tools_result = await session.list_tools()  # Get available tools from server
            return tools_result.tools
        
async def call_currency_tool(tool_name, tool_args):
    """Call a specific currency tool with given arguments."""
    async with stdio_client(params) as streams:  # Create stdio connection to MCP server
        async with mcp.ClientSession(*streams) as session:  # Initialize client session
            await session.initialize()  # Complete MCP handshake
            result = await session.call_tool(tool_name, tool_args)  # Execute tool with arguments
            return result
            
async def read_exchange_rate_resource(from_currency, to_currency):
    """Read exchange rate resource for two currencies."""
    async with stdio_client(params) as streams:  # Create stdio connection to MCP server
        async with mcp.ClientSession(*streams) as session:  # Initialize client session
            await session.initialize()  # Complete MCP handshake
            result = await session.read_resource(f"currency://rates/{from_currency}/{to_currency}")  # Read resource by URI
            return result.contents[0].text  # Extract text content from resource
        
async def read_supported_currencies_resource():
    """Read supported currencies resource."""
    async with stdio_client(params) as streams:  # Create stdio connection to MCP server
        async with mcp.ClientSession(*streams) as session:  # Initialize client session
            await session.initialize()  # Complete MCP handshake
            result = await session.read_resource("currency://supported")  # Read supported currencies resource
            return result.contents[0].text  # Extract text content from resource

async def get_currency_tools_openai():
    """Convert MCP currency tools to OpenAI-compatible tools."""
    openai_tools = []  # This list will store the OpenAI-compatible tools
    for tool in await list_currency_tools():  # Get all available MCP tools
        schema = {**tool.inputSchema, "additionalProperties": False}  # Convert MCP schema to OpenAI format
        
        # Ensure all properties are in the required array for OpenAI compatibility
        if "properties" in schema:
            all_properties = list(schema["properties"].keys())
            schema["required"] = all_properties  # Make all parameters required for OpenAI
        
        openai_tool = FunctionTool(  # Create OpenAI-compatible tool wrapper
            name=tool.name,
            description=tool.description,
            params_json_schema=schema,
            on_invoke_tool=lambda ctx, args, toolname=tool.name: call_currency_tool(toolname, json.loads(args))  # Function called when tool is invoked
        )
        openai_tools.append(openai_tool)
    return openai_tools  # Return list of OpenAI-compatible tools

# Convenience functions for common operations
async def get_exchange_rate(from_currency: str, to_currency: str, amount: float = 1.0):
    """Get exchange rate between two currencies."""
    result = await call_currency_tool("get_currency_rate", {
        "from_currency": from_currency,
        "to_currency": to_currency,
        "amount": amount
    })
    return result.content[0].text

async def convert_currency(amount: float, from_currency: str, to_currency: str):
    """Convert amount from one currency to another."""
    result = await call_currency_tool("convert_money", {
        "amount": amount,
        "from_currency": from_currency,
        "to_currency": to_currency
    })
    return result.content[0].text

async def get_supported_currencies():
    """Get list of supported currencies."""
    result = await call_currency_tool("get_supported_currencies", {})
    return result.content[0].text

async def get_multiple_rates(from_currency: str, to_currencies: str):
    """Get rates from one currency to multiple currencies."""
    result = await call_currency_tool("get_currency_rates", {
        "from_currency": from_currency,
        "to_currencies": to_currencies
    })
    return result.content[0].text