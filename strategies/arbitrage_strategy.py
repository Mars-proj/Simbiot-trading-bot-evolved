from utils.logging_setup import setup_logging

logger = setup_logging('arbitrage_strategy')

class ArbitrageStrategy:
    def __init__(self, market_state, market_data, volatility_analyzer):
        self.market_state = market_state
        self.market_data = market_data
        self.volatility_analyzer = volatility_analyzer
        self.price_diff_threshold = 0.02  # 2% порог для арбитража

    def adapt_parameters(self, symbol, timeframe, limit, exchange_name):
        """Adapt arbitrage threshold based on volatility."""
        try:
            klines = self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines for {symbol}, using default threshold")
                return
            volatility_factor = self.volatility_analyzer.analyze(klines)
            self.price_diff_threshold = 0.02 + 0.01 * volatility_factor  # Увеличиваем порог при высокой волатильности
            logger.info(f"Adapted price difference threshold for {symbol}: {self.price_diff_threshold}")
        except Exception as e:
            logger.error(f"Failed to adapt parameters for {symbol}: {str(e)}")

    def generate_signal(self, symbol, klines, timeframe, limit, exchange_name):
        """Generate an arbitrage signal (simplified)."""
        try:
            self.adapt_parameters(symbol, timeframe, limit, exchange_name)
            closes = [kline[4] for kline in klines][-2:]  # Последние два закрытия
            if len(closes) < 2:
                logger.warning(f"Not enough data for {symbol}")
                return None

            price_diff = (closes[-1] - closes[-2]) / closes[-2] if closes[-2] != 0 else 0
            if price_diff > self.price_diff_threshold:
                signal = "sell"
            elif price_diff < -self.price_diff_threshold:
                signal = "buy"
            else:
                signal = "hold"

            logger.info(f"Generated arbitrage signal for {symbol}: {signal}, price_diff={price_diff}")
            return {"symbol": symbol, "strategy": "arbitrage", "signal": signal, "entry_price": closes[-1], "trade_size": 100, "timeframe": timeframe, "limit": limit, "exchange_name": exchange_name}
        except Exception as e:
            logger.error(f"Failed to generate arbitrage signal for {symbol}: {str(e)}")
            return None
