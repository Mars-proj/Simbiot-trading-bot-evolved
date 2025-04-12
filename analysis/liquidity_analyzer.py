from trading_bot.logging_setup import setup_logging
from trading_bot.data_sources.market_data import MarketData

logger = setup_logging('liquidity_analyzer')

class LiquidityAnalyzer:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.market_data = MarketData(market_state)

    def analyze_liquidity(self, symbol: str, exchange_name: str = 'binance') -> float:
        """Analyze the liquidity of a symbol on the specified exchange."""
        try:
            # Получаем данные по объёму торгов для символа
            klines = self.market_data.get_klines(symbol, '1h', 24, exchange_name)  # Последние 24 часа
            if not klines:
                logger.warning(f"No klines data for {symbol} on {exchange_name}")
                return 0.0

            # Рассчитываем средний объём торгов (в USD)
            volumes = [kline['volume'] * kline['close'] for kline in klines]
            avg_volume = sum(volumes) / len(volumes) if volumes else 0.0

            # Динамическая корректировка на основе волатильности
            adjusted_volume = avg_volume * (1 - self.volatility / 2)

            logger.info(f"Liquidity for {symbol} on {exchange_name}: {adjusted_volume} USD")
            return adjusted_volume
        except Exception as e:
            logger.error(f"Failed to analyze liquidity for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    analyzer = LiquidityAnalyzer(market_state)
    symbols = analyzer.market_data.get_symbols('mexc')[:2]  # Первые 2 символа для теста с MEXC
    for symbol in symbols:
        liquidity = analyzer.analyze_liquidity(symbol, 'mexc')
        print(f"Liquidity for {symbol} on MEXC: {liquidity} USD")
