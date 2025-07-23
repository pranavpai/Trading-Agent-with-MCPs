# Import AsyncExitStack for managing multiple async context managers
from contextlib import AsyncExitStack
# Import MCP resource functions for account and strategy data
from accounts_client import read_accounts_resource, read_strategy_resource
# Import trace ID generation for debugging
from tracers import make_trace_id
# Import OpenAI Agents SDK core components
from agents import Agent, Tool, Runner, OpenAIChatCompletionsModel, trace
# Import OpenAI client for API communication
from openai import AsyncOpenAI
# Import environment variable loader
from dotenv import load_dotenv
# Import OS module for environment access
import os
# Import JSON parser for account data
import json
# Import MCP server stdio connector
from agents.mcp import MCPServerStdio
# Import instruction templates and message formatters
from templates import (
    researcher_instructions,
    trader_instructions,
    trade_message,
    rebalance_message,
    research_tool,
)
# Import MCP server configuration parameters
from mcp_params import trader_mcp_server_params, researcher_mcp_server_params

# Load environment variables, override existing values
load_dotenv(override=True)

# Get DeepSeek API key from environment
deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
# Get Google API key from environment  
google_api_key = os.getenv("GOOGLE_API_KEY")
# Get Grok API key from environment
grok_api_key = os.getenv("GROK_API_KEY")
# Get OpenRouter API key from environment
openrouter_api_key = os.getenv("OPENROUTER_API_KEY")

# DeepSeek API base URL
DEEPSEEK_BASE_URL = "https://api.deepseek.com/v1"
# Grok API base URL
GROK_BASE_URL = "https://api.x.ai/v1"
# Gemini API base URL (OpenAI-compatible endpoint)
GEMINI_BASE_URL = "https://generativelanguage.googleapis.com/v1beta/openai/"
# OpenRouter API base URL
OPENROUTER_BASE_URL = "https://openrouter.ai/api/v1"

# Maximum conversation turns to prevent infinite loops
MAX_TURNS = 30

# Create OpenAI client for OpenRouter models
openrouter_client = AsyncOpenAI(base_url=OPENROUTER_BASE_URL, api_key=openrouter_api_key)
# Create OpenAI client for DeepSeek models
deepseek_client = AsyncOpenAI(base_url=DEEPSEEK_BASE_URL, api_key=deepseek_api_key)
# Create OpenAI client for Grok models
grok_client = AsyncOpenAI(base_url=GROK_BASE_URL, api_key=grok_api_key)
# Create OpenAI client for Gemini models
gemini_client = AsyncOpenAI(base_url=GEMINI_BASE_URL, api_key=google_api_key)


# Factory function to get appropriate model client based on model name
def get_model(model_name: str):
    # OpenRouter models contain "/" in their name (e.g., "anthropic/claude-3-haiku")
    if "/" in model_name:
        return OpenAIChatCompletionsModel(model=model_name, openai_client=openrouter_client)
    # DeepSeek models contain "deepseek" in their name
    elif "deepseek" in model_name:
        return OpenAIChatCompletionsModel(model=model_name, openai_client=deepseek_client)
    # Grok models contain "grok" in their name
    elif "grok" in model_name:
        return OpenAIChatCompletionsModel(model=model_name, openai_client=grok_client)
    # Gemini models contain "gemini" in their name
    elif "gemini" in model_name:
        return OpenAIChatCompletionsModel(model=model_name, openai_client=gemini_client)
    # Default to OpenAI model name for standard models
    else:
        return model_name


# Create researcher agent with web search and analysis capabilities
async def get_researcher(mcp_servers, model_name) -> Agent:
    # Initialize Agent with name, instructions, model, and MCP servers
    researcher = Agent(
        name="Researcher",
        instructions=researcher_instructions(),  # Get instructions from template
        model=get_model(model_name),  # Get model client based on name
        mcp_servers=mcp_servers,  # Connect to MCP servers for tools
    )
    # Return configured researcher agent
    return researcher


# Convert researcher agent into a Tool for use by trader agents
async def get_researcher_tool(mcp_servers, model_name) -> Tool:
    # Get researcher agent instance
    researcher = await get_researcher(mcp_servers, model_name)
    # Convert to Tool using OpenAI Agents SDK as_tool() method
    return researcher.as_tool(tool_name="Researcher", tool_description=research_tool())


# Main Trader class for autonomous trading agents
class Trader:
    # Initialize trader with name, lastname, and model configuration
    def __init__(self, name: str, lastname="Trader", model_name="gpt-4o-mini"):
        # Trader's first name (used for account identification)
        self.name = name
        # Trader's last name for display purposes
        self.lastname = lastname
        # Agent instance (initially None, created later)
        self.agent = None
        # Model name for LLM selection
        self.model_name = model_name
        # Toggle between trading and rebalancing modes
        self.do_trade = True

    # Create the main trader agent with research capabilities
    async def create_agent(self, trader_mcp_servers, researcher_mcp_servers) -> Agent:
        # Get researcher tool for market analysis
        tool = await get_researcher_tool(researcher_mcp_servers, self.model_name)
        # Create trader agent with personalized instructions
        self.agent = Agent(
            name=self.name,  # Use trader's name for identification
            instructions=trader_instructions(self.name),  # Get personalized instructions
            model=get_model(self.model_name),  # Get model client
            tools=[tool],  # Provide researcher tool
            mcp_servers=trader_mcp_servers,  # Connect to trading MCP servers
        )
        # Return the configured agent
        return self.agent

    # Get simplified account report without time series data
    async def get_account_report(self) -> str:
        # Read account data from MCP resource
        account = await read_accounts_resource(self.name)
        # Parse JSON account data
        account_json = json.loads(account)
        # Remove time series data to reduce token usage
        account_json.pop("portfolio_value_time_series", None)
        # Return simplified account data as JSON string
        return json.dumps(account_json)

    # Execute the trader agent with current market context
    async def run_agent(self, trader_mcp_servers, researcher_mcp_servers):
        # Create agent with MCP server connections
        self.agent = await self.create_agent(trader_mcp_servers, researcher_mcp_servers)
        # Get current account status
        account = await self.get_account_report()
        # Read trading strategy from MCP resource
        strategy = await read_strategy_resource(self.name)
        # Choose message based on current mode (trade or rebalance)
        message = (
            trade_message(self.name, strategy, account)  # Active trading message
            if self.do_trade
            else rebalance_message(self.name, strategy, account)  # Portfolio rebalancing message
        )
        # Execute agent with message, limiting turns to prevent infinite loops
        await Runner.run(self.agent, message, max_turns=MAX_TURNS)

    # Manage MCP server connections using async context managers
    async def run_with_mcp_servers(self):
        # Use AsyncExitStack to manage multiple MCP server connections
        async with AsyncExitStack() as stack:
            # Create trader MCP server connections with 120s timeout
            trader_mcp_servers = [
                await stack.enter_async_context(
                    MCPServerStdio(params, client_session_timeout_seconds=120)
                )
                for params in trader_mcp_server_params
            ]
            # Nested context for researcher MCP servers
            async with AsyncExitStack() as stack:
                # Create researcher MCP server connections with 120s timeout
                researcher_mcp_servers = [
                    await stack.enter_async_context(
                        MCPServerStdio(params, client_session_timeout_seconds=120)
                    )
                    for params in researcher_mcp_server_params(self.name)
                ]
                # Run the agent with both server groups
                await self.run_agent(trader_mcp_servers, researcher_mcp_servers)

    # Execute trader with OpenAI tracing for debugging and monitoring
    async def run_with_trace(self):
        # Create descriptive trace name based on current mode
        trace_name = f"{self.name}-trading" if self.do_trade else f"{self.name}-rebalancing"
        # Generate unique trace ID for this trader
        trace_id = make_trace_id(f"{self.name.lower()}")
        # Use OpenAI Agents SDK trace context for debugging
        with trace(trace_name, trace_id=trace_id):
            # Run trader with MCP server management
            await self.run_with_mcp_servers()

    # Main entry point to run the trader with error handling
    async def run(self):
        try:
            # Execute trader with full tracing and error handling
            await self.run_with_trace()
        except Exception as e:
            # Log any errors that occur during execution
            print(f"Error running trader {self.name}: {e}")
        # Toggle between trading and rebalancing modes for next run
        self.do_trade = not self.do_trade
