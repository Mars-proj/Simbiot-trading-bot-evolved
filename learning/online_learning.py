from trading_bot.logging_setup import setup_logging
from trading_bot.models.base_model import BaseModel
from trading_bot.data_sources.market_data import MarketData
from trading_bot.symbol_filter import SymbolFilter

logger = setup_logging('online_learning')

class OnlineLearning:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.model = BaseModel(market_state)
        self.market_data = MarketData(market_state)

    def update_model(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'binance') -> None:
        """Update the model with new data."""
        try:
            # Получаем данные с биржи
            klines = self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines data for {symbol} on {exchange_name}")
                return

            # Формируем данные для обновления модели
            new_data = {
                'price': klines[-1]['close'],
                'volume': klines[-1]['volume'],
                'high': klines[-1]['high'],
                'low': klines[-1]['low']
            }

            # Динамическая корректировка данных на основе волатильности
            adjusted_data = {k: v * (1 + self.volatility / 2) if isinstance(v, (int, float)) else v for k, v in new_data.items()}
            
            self.model.update(adjusted_data)
            logger.info(f"Model updated with new data for {symbol}")
        except Exception as e:
            logger.error(f"Failed to update model for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    online_learning = OnlineLearning(market_state)
    symbol_filter = SymbolFilter(market_state)
    
    # Получаем символы
    symbols = symbol_filter.filter_symbols(online_learning.market_data.get_symbols('binance'), 'binance')
    
    if symbols:
        online_learning.update_model(symbols[0], '1h', 30, 'binance')
    else:
        print("No symbols available for testing")
