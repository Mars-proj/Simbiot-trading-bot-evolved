from trading_bot.logging_setup import setup_logging
from trading_bot.data_sources.market_data import MarketData

logger = setup_logging('risk_calculator')

class RiskCalculator:
    def __init__(self, market_state: dict, max_risk_per_trade: float = 0.02):
        self.volatility = market_state['volatility']
        self.max_risk_per_trade = max_risk_per_trade
        self.market_data = MarketData(market_state)

    def calculate_position_size(self, symbol: str, entry_price: float, stop_loss: float, account_balance: float, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'binance') -> float:
        """Calculate the position size based on risk parameters."""
        try:
            # Получаем данные для расчёта волатильности цены
            klines = self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines data for {symbol} on {exchange_name}")
                return 0.0

            # Рассчитываем риск на основе волатильности
            risk_amount = account_balance * self.max_risk_per_trade
            price_diff = abs(entry_price - stop_loss)
            if price_diff == 0:
                logger.warning("Price difference is zero, cannot calculate position size")
                return 0.0

            position_size = risk_amount / price_diff
            
            # Динамическая корректировка на основе волатильности
            adjusted_position_size = position_size * (1 - self.volatility / 2)
            
            logger.info(f"Calculated position size for {symbol}: {adjusted_position_size}")
            return adjusted_position_size
        except Exception as e:
            logger.error(f"Failed to calculate position size for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    from trading_bot.symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    calculator = RiskCalculator(market_state)
    symbol_filter = SymbolFilter(market_state)
    
    # Получаем символы
    symbols = symbol_filter.filter_symbols(calculator.market_data.get_symbols('binance'), 'binance')
    
    if symbols:
        # Получаем последнюю цену
        klines = calculator.market_data.get_klines(symbols[0], '1h', 1, 'binance')
        if klines:
            entry_price = klines[-1]['close']
            stop_loss = entry_price * 0.95  # 5% ниже
            account_balance = 10000
            position_size = calculator.calculate_position_size(symbols[0], entry_price, stop_loss, account_balance)
            print(f"Position size for {symbols[0]}: {position_size}")
        else:
            print(f"No klines data for {symbols[0]}")
    else:
        print("No symbols available for testing")
