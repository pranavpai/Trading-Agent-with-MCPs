from accounts import Account

for name in ['Warren', 'George', 'Ray', 'Cathie']:
    account = Account.get(name)
    portfolio_value = account.calculate_portfolio_value() or 0
    transactions = account.list_transactions()
    holdings = account.get_holdings()
    
    print(f"{name}:")
    print(f"  Balance: ${account.balance:.2f}")
    print(f"  Portfolio Value: ${portfolio_value:.2f}")
    print(f"  Transactions: {len(transactions)}")
    print(f"  Holdings: {len(holdings) if holdings else 0}")
    print(f"  Portfolio History Points: {len(account.portfolio_value_time_series)}")
    
    if len(account.portfolio_value_time_series) > 0:
        print(f"  Latest Portfolio Value: {account.portfolio_value_time_series[-1]}")
    print()
