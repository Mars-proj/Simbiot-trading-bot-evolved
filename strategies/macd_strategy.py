import numpy as np
from utils.logging_setup import setup_logging

logger = setup_logging('macd_strategy')

class MACDStrategy:
    def __init__(self, market_state, market_data, volatility_analyzer, fast_period=12, slow_period=26, signal_period=9):
        self.market_state = market_state
        self.market_data = market_data
        self.volatility_analyzer = volatility_analyzer
        self.fast_period = fast_period
        self.slow_period = slow_period
        self.signal_period = signal_period
        self.base_fast_period = fast_period
        self.base_slow_period = slow_period

    async def adapt_parameters(self, symbol, timeframe, limit, exchange_name):
        """Adapt MACD periods based on market volatility."""
        try:
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines for {symbol}, using default MACD periods")
                return
            volatility_factor = self.volatility_analyzer.analyze(klines)
            self.fast_period = int(self.base_fast_period * (1 + volatility_factor))
            self.slow_period = int(self.base_slow_period * (1 + volatility_factor))
            logger.info(f"Adapted MACD periods for {symbol}: fast={self.fast_period}, slow={self.slow_period}")
        except Exception as e:
            logger.error(f"Failed to adapt parameters for {symbol}: {str(e)}")

    def calculate_ema(self, closes, period):
        ema = [closes[0]]
        k = 2 / (period + 1)
        for price in closes[1:]:
            ema.append(price * k + ema[-1] * (1 - k))
        return ema

    async def generate_signal(self, symbol, klines, timeframe, limit, exchange_name):
        """Generate a signal using MACD."""
        try:
            await self.adapt_parameters(symbol, timeframe, limit, exchange_name)
            closes = [kline[4] for kline in klines][-self.slow_period*2:]
            if len(closes) < self.slow_period:
                logger.warning(f"Not enough data for {symbol}")
                return None

            fast_ema = self.calculate_ema(closes, self.fast_period)
            slow_ema = self.calculate_ema(closes, self.slow_period)
            macd = [f - s for f, s in zip(fast_ema, slow_ema)]
            signal_line = self.calculate_ema(macd, self.signal_period)

            if len(macd) < 2 or len(signal_line) < 2:
                return None

            if macd[-1] > signal_line[-1] and macd[-2] <= signal_line[-2]:
                signal = "buy"
            elif macd[-1] < signal_line[-1] and macd[-2] >= signal_line[-2]:
                signal = "sell"
            else:
                signal = "hold"

            logger.info(f"Generated MACD signal for {symbol}: {signal}")
            return {"symbol": symbol, "strategy": "macd", "signal": signal, "entry_price": closes[-1], "trade_size": 100, "timeframe": timeframe, "limit": limit, "exchange_name": exchange_name}
        except Exception as e:
            logger.error(f"Failed to generate MACD signal for {symbol}: {str(e)}")
            return None
