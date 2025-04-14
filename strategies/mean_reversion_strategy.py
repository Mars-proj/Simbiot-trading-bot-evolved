import numpy as np
from utils.logging_setup import setup_logging

logger = setup_logging('mean_reversion_strategy')

class MeanReversionStrategy:
    def __init__(self, market_state, market_data, volatility_analyzer):
        self.market_state = market_state
        self.market_data = market_data
        self.volatility_analyzer = volatility_analyzer
        self.lookback_period = 20
        self.z_score_threshold = 2

    def adapt_parameters(self, symbol, timeframe, limit, exchange_name):
        """Adapt z-score threshold based on volatility."""
        try:
            klines = self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines for {symbol}, using default z-score threshold")
                return
            volatility_factor = self.volatility_analyzer.analyze(klines)
            self.z_score_threshold = 2 + volatility_factor  # Увеличиваем порог при высокой волатильности
            logger.info(f"Adapted z-score threshold for {symbol}: {self.z_score_threshold}")
        except Exception as e:
            logger.error(f"Failed to adapt parameters for {symbol}: {str(e)}")

    def generate_signal(self, symbol, klines, timeframe, limit, exchange_name):
        """Generate a mean reversion signal."""
        try:
            self.adapt_parameters(symbol, timeframe, limit, exchange_name)
            closes = [kline[4] for kline in klines][-self.lookback_period:]
            if len(closes) < self.lookback_period:
                logger.warning(f"Not enough data for {symbol}")
                return None

            mean = np.mean(closes)
            std = np.std(closes)
            z_score = (closes[-1] - mean) / std if std != 0 else 0

            if z_score > self.z_score_threshold:
                signal = "sell"
            elif z_score < -self.z_score_threshold:
                signal = "buy"
            else:
                signal = "hold"

            logger.info(f"Generated mean reversion signal for {symbol}: {signal}, z_score={z_score}")
            return {"symbol": symbol, "strategy": "mean_reversion", "signal": signal, "entry_price": closes[-1], "trade_size": 100, "timeframe": timeframe, "limit": limit, "exchange_name": exchange_name}
        except Exception as e:
            logger.error(f"Failed to generate mean reversion signal for {symbol}: {str(e)}")
            return None
