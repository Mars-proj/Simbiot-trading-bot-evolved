from utils.logging_setup import setup_logging

logger = setup_logging('volatility_strategy')

class VolatilityStrategy:
    def __init__(self, market_state, market_data, volatility_analyzer):
        self.market_state = market_state
        self.market_data = market_data
        self.volatility_analyzer = volatility_analyzer
        self.volatility_threshold = 0.05  # 5% по умолчанию

    def adapt_parameters(self, symbol, timeframe, limit, exchange_name):
        """Adapt volatility threshold dynamically."""
        try:
            klines = self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines for {symbol}, using default volatility threshold")
                return
            volatility = self.volatility_analyzer.analyze(klines)
            self.volatility_threshold = volatility * 1.2  # Увеличиваем порог на основе текущей волатильности
            logger.info(f"Adapted volatility threshold for {symbol}: {self.volatility_threshold}")
        except Exception as e:
            logger.error(f"Failed to adapt parameters for {symbol}: {str(e)}")

    def generate_signal(self, symbol, klines, timeframe, limit, exchange_name):
        """Generate a volatility-based signal."""
        try:
            self.adapt_parameters(symbol, timeframe, limit, exchange_name)
            volatility = self.volatility_analyzer.analyze(klines)
            current_price = klines[-1][4]  # Последняя цена закрытия

            if volatility > self.volatility_threshold:
                signal = "hold"  # Высокая волатильность — ждём
            else:
                # Простая логика: покупаем, если волатильность низкая
                signal = "buy"

            logger.info(f"Generated volatility signal for {symbol}: {signal}, volatility={volatility}")
            return {"symbol": symbol, "strategy": "volatility", "signal": signal, "entry_price": current_price, "trade_size": 100, "timeframe": timeframe, "limit": limit, "exchange_name": exchange_name}
        except Exception as e:
            logger.error(f"Failed to generate volatility signal for {symbol}: {str(e)}")
            return None
