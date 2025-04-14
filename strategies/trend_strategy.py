import numpy as np
from utils.logging_setup import setup_logging

logger = setup_logging('trend_strategy')

class TrendStrategy:
    def __init__(self, market_state, market_data, volatility_analyzer):
        self.market_state = market_state
        self.market_data = market_data
        self.volatility_analyzer = volatility_analyzer
        self.lookback_period = 50

    def adapt_parameters(self, symbol, timeframe, limit, exchange_name):
        """Adapt lookback period based on volatility."""
        try:
            klines = self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines for {symbol}, using default lookback period")
                return
            volatility_factor = self.volatility_analyzer.analyze(klines)
            self.lookback_period = int(50 * (1 + volatility_factor))  # Увеличиваем период при высокой волатильности
            logger.info(f"Adapted lookback period for {symbol}: {self.lookback_period}")
        except Exception as e:
            logger.error(f"Failed to adapt parameters for {symbol}: {str(e)}")

    def generate_signal(self, symbol, klines, timeframe, limit, exchange_name):
        """Generate a trend-following signal."""
        try:
            self.adapt_parameters(symbol, timeframe, limit, exchange_name)
            closes = [kline[4] for kline in klines][-self.lookback_period:]
            if len(closes) < self.lookback_period:
                logger.warning(f"Not enough data for {symbol}")
                return None

            short_ma = np.mean(closes[-10:])  # Короткая скользящая средняя
            long_ma = np.mean(closes)  # Длинная скользящая средняя
            if short_ma > long_ma:
                signal = "buy"
            elif short_ma < long_ma:
                signal = "sell"
            else:
                signal = "hold"

            logger.info(f"Generated trend signal for {symbol}: {signal}")
            return {"symbol": symbol, "strategy": "trend", "signal": signal, "entry_price": closes[-1], "trade_size": 100, "timeframe": timeframe, "limit": limit, "exchange_name": exchange_name}
        except Exception as e:
            logger.error(f"Failed to generate trend signal for {symbol}: {str(e)}")
            return None
