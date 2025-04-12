from trading_bot.logging_setup import setup_logging

logger = setup_logging('symbol_filter')

class SymbolFilter:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.filters = []

    def add_filter(self, filter_func):
        """Add a filter function for symbols."""
        try:
            self.filters.append(filter_func)
            logger.info("Filter added to SymbolFilter")
        except Exception as e:
            logger.error(f"Failed to add filter: {str(e)}")
            raise

    def filter_symbols(self, symbols: list) -> list:
        """Filter symbols based on defined filters."""
        try:
            filtered_symbols = symbols.copy()
            for filter_func in self.filters:
                # Динамическая корректировка фильтра на основе волатильности
                adjusted_filter = lambda symbol: filter_func(symbol, volatility=self.volatility)
                filtered_symbols = [symbol for symbol in filtered_symbols if adjusted_filter(symbol)]
            
            logger.info(f"Filtered symbols: {filtered_symbols}")
            return filtered_symbols
        except Exception as e:
            logger.error(f"Failed to filter symbols: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    symbol_filter = SymbolFilter(market_state)

    # Пример фильтра: символы с высокой ликвидностью
    def liquidity_filter(symbol, volatility):
        # Условный критерий: ликвидность выше порога, скорректированного на волатильность
        liquidity_threshold = 1000000 * (1 - volatility / 2)
        symbol_liquidity = 1500000 if 'BTC' in symbol else 500000
        return symbol_liquidity > liquidity_threshold

    symbol_filter.add_filter(liquidity_filter)
    symbols = ['BTC/USDT', 'ETH/USDT', 'LTC/USDT']
    filtered = symbol_filter.filter_symbols(symbols)
    print(f"Filtered symbols: {filtered}")
