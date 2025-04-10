from typing import Dict
from strategies import Strategy
from learning.trade_evaluator import evaluate_trades
from logging_setup import setup_logging

logger = setup_logging('learning_backtester')

def backtest(strategy: Strategy, data: dict) -> dict:
    """Run a backtest in the learning module with detailed analytics."""
    try:
        trades = []
        balance = 10000  # Starting balance
        position = None

        for timestamp, price in data.items():
            signal = strategy.generate_signal(price, pd.DataFrame(data))
            if signal == "buy" and position is None:
                position = {"buy_price": price, "timestamp": timestamp}
                trades.append({"type": "buy", "price": price, "timestamp": timestamp})
            elif signal == "sell" and position:
                profit = price - position["buy_price"]
                balance += profit
                trades.append({"type": "sell", "price": price, "timestamp": timestamp, "profit": profit})
                position = None

        # Evaluate trades
        evaluation = evaluate_trades(trades)
        evaluation["final_balance"] = balance
        logger.info(f"Backtest completed: {evaluation}")
        return evaluation
    except Exception as e:
        logger.error(f"Backtest failed: {str(e)}")
        raise
