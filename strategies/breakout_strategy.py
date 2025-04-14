from utils.logging_setup import setup_logging

logger = setup_logging('breakout_strategy')

class BreakoutStrategy:
    def __init__(self, market_state, market_data, volatility_analyzer):
        self.market_state = market_state
        self.market_data = market_data
        self.volatility_analyzer = volatility_analyzer
        self.lookback_period = 20
        self.breakout_threshold = 0.03  # 3% по умолчанию

    def adapt_parameters(self, symbol, timeframe, limit, exchange_name):
        """Adapt breakout threshold based on volatility."""
        try:
            klines = self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines for {symbol}, using default breakout threshold")
                return
            volatility_factor = self.volatility_analyzer.analyze(klines)
            self.breakout_threshold = 0.03 * (1 + volatility_factor)  # Увеличиваем порог при высокой волатильности
            logger.info(f"Adapted breakout threshold for {symbol}: {self.breakout_threshold}")
        except Exception as e:
            logger.error(f"Failed to adapt parameters for {symbol}: {str(e)}")

    def generate_signal(self, symbol, klines, timeframe, limit, exchange_name):
        """Generate a breakout signal."""
        try:
            self.adapt_parameters(symbol, timeframe, limit, exchange_name)
            highs = [kline[2] for kline in klines][-self.lookback_period:]  # Максимумы
            lows = [kline[3] for kline in klines][-self.lookback_period:]  # Минимумы
            current_price = klines[-1][4]  # Последняя цена закрытия

            if len(highs) < self.lookback_period:
                logger.warning(f"Not enough data for {symbol}")
                return None

            resistance = max(highs[:-1])
            support = min(lows[:-1])
            breakout_up = current_price > resistance * (1 + self.breakout_threshold)
            breakout_down = current_price < support * (1 - self.breakout_threshold)

            if breakout_up:
                signal = "buy"
            elif breakout_down:
                signal = "sell"
            else:
                signal = "hold"

            logger.info(f"Generated breakout signal for {symbol}: {signal}")
            return {"symbol": symbol, "strategy": "breakout", "signal": signal, "entry_price": current_price, "trade_size": 100, "timeframe": timeframe, "limit": limit, "exchange_name": exchange_name}
        except Exception as e:
            logger.error(f"Failed to generate breakout signal for {symbol}: {str(e)}")
            return None
