# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## System Overview

This is a distributed multi-agent trading system that uses Model Context Protocol (MCP) servers to enable AI trading agents to interact with financial markets. The system simulates autonomous trading with 4 different AI trader personalities using various LLM models.

## Key Commands

### Starting the System
```bash
# Initialize/reset trader accounts (required before first run)
python reset.py

# Start the main trading system (runs continuously)
python trading_floor.py

# Start web dashboard for monitoring (separate terminal)
python app.py
```

### Development Setup
```bash
# Install dependencies
uv sync

# Check environment configuration
python -c "import os; print('OPENAI_API_KEY:', 'SET' if os.getenv('OPENAI_API_KEY') else 'MISSING')"
```

### Database Operations
```bash
# Reset all accounts to initial state
python reset.py

# Inspect database directly
sqlite3 accounts.db
```

## Architecture

### Distributed MCP Server Model
The system uses multiple MCP servers running as separate processes:

- **Accounts Server** (`accounts_server.py`) - Trading operations (buy/sell, balance, holdings)
- **Market Server** (`market_server.py`) - Stock price data via Polygon API
- **Push Server** (`push_server.py`) - Notifications via Pushover
- **Research Servers** - Web fetch, Brave search, and persistent memory per trader

### Main Execution Flow
1. **Trading Floor** (`trading_floor.py`) orchestrates 4 traders on a schedule (default: 60 minutes)
2. Each **Trader** (`traders.py`) alternates between "trading" and "rebalancing" modes
3. Traders use **Researcher agents** to gather market intelligence via MCP servers
4. Trading decisions executed through **Accounts MCP server** → SQLite database
5. **Web Dashboard** (`app.py`) provides real-time monitoring via Gradio

### Data Architecture
- **SQLite Database** (`accounts.db`) - Persistent storage for accounts, transactions, logs
- **Account Objects** (`accounts.py`) - Pydantic models for portfolio management
- **Market Data** (`market.py`) - Polygon API integration with fallback to simulated prices

## Configuration

### Required Environment Variables
```bash
OPENAI_API_KEY=your_key_here        # Primary AI model access
POLYGON_API_KEY=your_key_here       # Market data (optional, has fallback)
BRAVE_API_KEY=your_key_here         # Web search for research
PUSHOVER_USER=your_user_key         # Push notifications
PUSHOVER_TOKEN=your_app_token       # Push notifications
```

### Optional Configuration
```bash
RUN_EVERY_N_MINUTES=60                    # Trading frequency
RUN_EVEN_WHEN_MARKET_IS_CLOSED=false     # Weekend/holiday trading
USE_MANY_MODELS=false                     # Single vs multiple AI models
POLYGON_PLAN=free                         # API tier: free|paid|realtime
```

## Trader Personalities

Each trader has distinct investment philosophy defined in `reset.py`:
- **Warren** - Value investing, long-term approach
- **George** - Macro trading, contrarian strategies  
- **Ray** - Systematic, diversified risk management
- **Cathie** - Growth/innovation focus, crypto ETFs

## Database Schema

Key tables in `accounts.db`:
- **accounts** - Current portfolio state (balance, holdings)
- **logs** - Trading activity and decision logs
- **market** - Cached market data

## Debugging

### MCP Server Issues
```bash
# Test individual MCP servers
python accounts_server.py
python market_server.py
```

### Database Inspection
```bash
sqlite3 accounts.db
.tables
SELECT * FROM accounts;
SELECT * FROM logs ORDER BY timestamp DESC LIMIT 10;
```

### Enable Detailed Logging
Set `LANGSMITH_TRACING=true` in `.env` for AI conversation tracing.

## Key Design Patterns

- **Agent Architecture**: Each trader combines trading logic with researcher capabilities
- **MCP Integration**: Tools distributed across multiple servers for scalability
- **Fault Tolerance**: Traders operate independently with comprehensive error handling
- **Observable System**: All decisions logged with real-time web dashboard
- **Model Flexibility**: Support for OpenAI, DeepSeek, Gemini, Grok models via `USE_MANY_MODELS`

## File Structure Context

- `trading_floor.py` - Main orchestrator and scheduler
- `traders.py` - Core trader agent implementation
- `accounts.py` - Portfolio management with Pydantic models
- `market.py` - Market data integration (Polygon API)
- `database.py` - SQLite operations and schema
- `app.py` - Gradio web dashboard
- `*_server.py` - Individual MCP servers for distributed tools
- `templates.py` - Agent prompts and instructions