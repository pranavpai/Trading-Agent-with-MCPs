from mcp.server.fastmcp import FastMCP
from currency_rates import get_exchange_rate, convert_currency, list_supported_currencies, get_multiple_rates

mcp = FastMCP("currency_server")

@mcp.tool()
async def get_currency_rate(from_currency: str, to_currency: str, amount: float = 1.0) -> str:
    """Get the exchange rate between two currencies.

    Args:
        from_currency: The base currency code (e.g., USD, EUR)
        to_currency: The target currency code (e.g., EUR, JPY) 
        amount: The amount to convert (defaults to 1.0)
    """
    return get_exchange_rate(from_currency, to_currency, amount)

@mcp.tool()
async def convert_money(amount: float, from_currency: str, to_currency: str) -> str:
    """Convert an amount from one currency to another.

    Args:
        amount: The amount to convert
        from_currency: The source currency code (e.g., USD, EUR)
        to_currency: The target currency code (e.g., EUR, JPY)
    """
    return convert_currency(amount, from_currency, to_currency)

@mcp.tool()
async def get_supported_currencies() -> str:
    """Get the list of supported currency codes.
    
    Returns a JSON string with all supported currencies.
    """
    return list_supported_currencies()

@mcp.tool()
async def get_currency_rates(from_currency: str, to_currencies: str) -> str:
    """Get exchange rates from one currency to multiple target currencies.

    Args:
        from_currency: The base currency code (e.g., USD)
        to_currencies: Comma-separated list of target currencies (e.g., "EUR,GBP,JPY")
    """
    return get_multiple_rates(from_currency, to_currencies)

@mcp.resource("currency://rates/{from_currency}/{to_currency}")
async def read_exchange_rate_resource(from_currency: str, to_currency: str) -> str:
    """Resource to get exchange rate information between two currencies."""
    return get_exchange_rate(from_currency, to_currency, 1.0)

@mcp.resource("currency://supported")
async def read_supported_currencies_resource() -> str:
    """Resource to get the list of supported currencies."""
    return list_supported_currencies()

if __name__ == "__main__":
    mcp.run(transport='stdio')