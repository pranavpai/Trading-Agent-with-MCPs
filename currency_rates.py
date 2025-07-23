import requests
import json
from typing import Dict, List, Optional
from datetime import datetime, timedelta
import os

class CurrencyExchangeService:
    def __init__(self):
        self.api_key = os.getenv('EXCHANGE_API_KEY')
        self.base_url = "https://api.exchangerate-api.io/v4/latest"
        self.fallback_rates = {
            'USD': {
                'EUR': 0.85, 'GBP': 0.73, 'JPY': 110.0, 'CAD': 1.25, 
                'AUD': 1.35, 'CHF': 0.92, 'CNY': 6.45, 'INR': 75.0
            },
            'EUR': {
                'USD': 1.18, 'GBP': 0.86, 'JPY': 129.5, 'CAD': 1.47,
                'AUD': 1.59, 'CHF': 1.08, 'CNY': 7.59, 'INR': 88.2
            }
        }
        self.supported_currencies = ['USD', 'EUR', 'GBP', 'JPY', 'CAD', 'AUD', 'CHF', 'CNY', 'INR']
    
    def _get_fallback_rate(self, from_currency: str, to_currency: str) -> float:
        if from_currency == to_currency:
            return 1.0
        
        if from_currency in self.fallback_rates and to_currency in self.fallback_rates[from_currency]:
            return self.fallback_rates[from_currency][to_currency]
        elif to_currency in self.fallback_rates and from_currency in self.fallback_rates[to_currency]:
            return 1.0 / self.fallback_rates[to_currency][from_currency]
        else:
            raise ValueError(f"Exchange rate not available for {from_currency} to {to_currency}")
    
    def get_exchange_rate(self, from_currency: str, to_currency: str, amount: float = 1.0) -> Dict:
        from_currency = from_currency.upper()
        to_currency = to_currency.upper()
        
        if from_currency not in self.supported_currencies:
            raise ValueError(f"Currency {from_currency} is not supported")
        if to_currency not in self.supported_currencies:
            raise ValueError(f"Currency {to_currency} is not supported")
        
        try:
            url = f"{self.base_url}/{from_currency}"
            response = requests.get(url, timeout=5)
            
            if response.status_code == 200:
                data = response.json()
                if 'rates' in data and to_currency in data['rates']:
                    rate = data['rates'][to_currency]
                    converted_amount = amount * rate
                    return {
                        'from_currency': from_currency,
                        'to_currency': to_currency,
                        'rate': rate,
                        'amount': amount,
                        'converted_amount': converted_amount,
                        'timestamp': datetime.now().isoformat(),
                        'source': 'api'
                    }
        except Exception as e:
            print(f"API request failed: {e}, using fallback data")
        
        rate = self._get_fallback_rate(from_currency, to_currency)
        converted_amount = amount * rate
        return {
            'from_currency': from_currency,
            'to_currency': to_currency,
            'rate': rate,
            'amount': amount,
            'converted_amount': converted_amount,
            'timestamp': datetime.now().isoformat(),
            'source': 'fallback'
        }
    
    def convert_currency(self, amount: float, from_currency: str, to_currency: str) -> Dict:
        return self.get_exchange_rate(from_currency, to_currency, amount)
    
    def list_supported_currencies(self) -> List[str]:
        return self.supported_currencies.copy()
    
    def get_multiple_rates(self, from_currency: str, to_currencies: List[str]) -> Dict:
        from_currency = from_currency.upper()
        rates = {}
        
        for to_currency in to_currencies:
            try:
                result = self.get_exchange_rate(from_currency, to_currency)
                rates[to_currency] = result['rate']
            except Exception as e:
                rates[to_currency] = f"Error: {str(e)}"
        
        return {
            'base_currency': from_currency,
            'rates': rates,
            'timestamp': datetime.now().isoformat()
        }

currency_service = CurrencyExchangeService()

def get_exchange_rate(from_currency: str, to_currency: str, amount: float = 1.0) -> str:
    try:
        result = currency_service.get_exchange_rate(from_currency, to_currency, amount)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e)}, indent=2)

def convert_currency(amount: float, from_currency: str, to_currency: str) -> str:
    try:
        result = currency_service.convert_currency(amount, from_currency, to_currency)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e)}, indent=2)

def list_supported_currencies() -> str:
    try:
        currencies = currency_service.list_supported_currencies()
        return json.dumps({
            'supported_currencies': currencies,
            'count': len(currencies),
            'timestamp': datetime.now().isoformat()
        }, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e)}, indent=2)

def get_multiple_rates(from_currency: str, to_currencies: str) -> str:
    try:
        to_list = [c.strip().upper() for c in to_currencies.split(',')]
        result = currency_service.get_multiple_rates(from_currency, to_list)
        return json.dumps(result, indent=2)
    except Exception as e:
        return json.dumps({'error': str(e)}, indent=2)

if __name__ == "__main__":
    print(get_exchange_rate("USD", "EUR", 100))
    print(convert_currency(50, "EUR", "JPY"))
    print(list_supported_currencies())