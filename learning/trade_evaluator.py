import numpy as np

def evaluate_trades(trades: list) -> dict:
    """Evaluate trades and calculate metrics."""
    if not trades:
        return {"profit": 0.0, "max_drawdown": 0.0, "sharpe_ratio": 0.0}

    # Calculate total profit
    profits = [t['profit'] for t in trades if 'profit' in t]
    total_profit = sum(profits)

    # Calculate returns for Sharpe ratio
    returns = np.array(profits)
    mean_return = np.mean(returns)
    std_return = np.std(returns) if len(returns) > 1 else 0.0
    sharpe_ratio = mean_return / std_return if std_return != 0 else 0.0

    # Calculate maximum drawdown
    balance = 10000  # Starting balance
    peak = balance
    max_drawdown = 0.0
    for trade in trades:
        if 'profit' in trade:
            balance += trade['profit']
            peak = max(peak, balance)
            drawdown = (peak - balance) / peak if peak != 0 else 0.0
            max_drawdown = max(max_drawdown, drawdown)

    return {
        "profit": total_profit,
        "max_drawdown": max_drawdown,
        "sharpe_ratio": sharpe_ratio
    }
