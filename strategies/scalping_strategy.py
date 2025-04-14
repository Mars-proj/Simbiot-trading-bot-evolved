from utils.logging_setup import setup_logging

logger = setup_logging('scalping_strategy')

class ScalpingStrategy:
    def __init__(self, market_state, market_data, volatility_analyzer):
        self.market_state = market_state
        self.market_data = market_data
        self.volatility_analyzer = volatility_analyzer
        self.scalp_range = 0.005  # 0.5% по умолчанию

    def adapt_parameters(self, symbol, timeframe, limit, exchange_name):
        """Adapt scalp range based on volatility."""
        try:
            klines = self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines for {symbol}, using default scalp range")
                return
            volatility_factor = self.volatility_analyzer.analyze(klines)
            self.scalp_range = 0.005 * (1 + volatility_factor)  # Увеличиваем диапазон при высокой волатильности
            logger.info(f"Adapted scalp range for {symbol}: {self.scalp_range}")
        except Exception as e:
            logger.error(f"Failed to adapt parameters for {symbol}: {str(e)}")

    def generate_signal(self, symbol, klines, timeframe, limit, exchange_name):
        """Generate a scalping signal (simplified)."""
        try:
            self.adapt_parameters(symbol, timeframe, limit, exchange_name)
            closes = [kline[4] for kline in klines][-2:]  # Последние две цены
            if len(closes) < 2:
                logger.warning(f"Not enough data for {symbol}")
                return None

            price_change = (closes[-1] - closes[-2]) / closes[-2] if closes[-2] != 0 else 0
            if price_change > self.scalp_range:
                signal = "sell"
            elif price_change < -self.scalp_range:
                signal = "buy"
            else:
                signal = "hold"

            logger.info(f"Generated scalping signal for {symbol}: {signal}")
            return {"symbol": symbol, "strategy": "scalping", "signal": signal, "entry_price": closes[-1], "trade_size": 100, "timeframe": timeframe, "limit": limit, "exchange_name": exchange_name}
        except Exception as e:
            logger.error(f"Failed to generate scalping signal for {symbol}: {str(e)}")
            return None
