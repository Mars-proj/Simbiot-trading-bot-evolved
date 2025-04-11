from trading_bot.logging_setup import setup_logging
from trading_bot.strategies.strategy_manager import StrategyManager

logger = setup_logging('backtester')

class Backtester:
    def __init__(self, market_state: dict, account_balance: float = 10000):
        self.volatility = market_state['volatility']
        self.account_balance = account_balance
        self.strategy_manager = StrategyManager(market_state)

    def run_backtest(self, klines: list, strategy_name: str) -> dict:
        """Run a backtest for the specified strategy."""
        try:
            if not klines:
                logger.warning("No kline data provided for backtest")
                return {'status': 'failed', 'reason': 'no data'}

            # Добавляем стратегию в менеджер
            self.strategy_manager.add_strategy(strategy_name)
            
            # Генерируем сигналы
            signals = self.strategy_manager.generate_signals(klines)[strategy_name]
            
            # Симулируем сделки
            balance = self.account_balance
            positions = []
            for signal in signals:
                if signal['signal'] == 'buy':
                    # Покупаем актив
                    quantity = (balance * 0.1) / klines[signal['timestamp']]['close']  # 10% баланса
                    positions.append({
                        'entry_price': klines[signal['timestamp']]['close'],
                        'quantity': quantity
                    })
                    balance -= quantity * klines[signal['timestamp']]['close']
                elif signal['signal'] == 'sell' and positions:
                    # Продаём актив
                    position = positions.pop(0)
                    profit = (klines[signal['timestamp']]['close'] - position['entry_price']) * position['quantity']
                    balance += position['quantity'] * klines[signal['timestamp']]['close']
            
            result = {
                'final_balance': balance,
                'profit': balance - self.account_balance,
                'positions': positions
            }
            logger.info(f"Backtest result: {result}")
            return result
        except Exception as e:
            logger.error(f"Failed to run backtest: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    backtester = Backtester(market_state)
    klines = [{'timestamp': i, 'close': float(50000 + i * 100)} for i in range(30)]
    result = backtester.run_backtest(klines, 'bollinger')
    print(f"Backtest result: {result}")
