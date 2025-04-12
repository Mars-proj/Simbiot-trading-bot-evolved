from trading_bot.logging_setup import setup_logging
from trading_bot.analysis.liquidity_analyzer import LiquidityAnalyzer
from trading_bot.analysis.volatility_analyzer import VolatilityAnalyzer

logger = setup_logging('symbol_filter')

class SymbolFilter:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.liquidity_analyzer = LiquidityAnalyzer(market_state)
        self.volatility_analyzer = VolatilityAnalyzer(market_state)
        self.filters = []

    def add_filter(self, filter_func):
        """Add a filter function for symbols."""
        try:
            self.filters.append(filter_func)
            logger.info("Filter added to SymbolFilter")
        except Exception as e:
            logger.error(f"Failed to add filter: {str(e)}")
            raise

    def filter_symbols(self, symbols: list, exchange_name: str = 'binance') -> list:
        """Filter symbols based on defined filters."""
        try:
            filtered_symbols = symbols.copy()
            for filter_func in self.filters:
                filtered_symbols = [symbol for symbol in filtered_symbols if filter_func(symbol, exchange_name)]
            
            logger.info(f"Filtered symbols: {filtered_symbols}")
            return filtered_symbols
        except Exception as e:
            logger.error(f"Failed to filter symbols: {str(e)}")
            raise

    def setup_default_filters(self, min_liquidity: float = 1000000, max_volatility: float = 0.5):
        """Set up default filters for liquidity and volatility."""
        def liquidity_filter(symbol, exchange_name):
            liquidity = self.liquidity_analyzer.analyze_liquidity(symbol, exchange_name)
            # Динамическая корректировка порога ликвидности на основе волатильности
            adjusted_threshold = min_liquidity * (1 - self.volatility / 2)
            return liquidity > adjusted_threshold

        def volatility_filter(symbol, exchange_name):
            symbol_volatility = self.volatility_analyzer.analyze_volatility(symbol, exchange_name)
            # Динамическая корректировка порога волатильности на основе текущей волатильности рынка
            adjusted_threshold = max_volatility + self.volatility
            return symbol_volatility < adjusted_threshold

        self.add_filter(liquidity_filter)
        self.add_filter(volatility_filter)

if __name__ == "__main__":
    # Test run
    from trading_bot.data_sources.market_data import MarketData
    market_state = {'volatility': 0.3}
    symbol_filter = SymbolFilter(market_state)
    market_data = MarketData(market_state)
    
    # Получаем реальные символы с биржи
    symbols = market_data.get_symbols('binance')
    
    # Применяем фильтры
    symbol_filter.setup_default_filters(min_liquidity=1000000, max_volatility=0.5)
    filtered = symbol_filter.filter_symbols(symbols, 'binance')
    print(f"Filtered symbols: {filtered[:5]}")  # Первые 5 символов для теста
