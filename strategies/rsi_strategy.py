import numpy as np
from utils.logging_setup import setup_logging

logger = setup_logging('rsi_strategy')

class RSIStrategy:
    def __init__(self, market_state, market_data, volatility_analyzer, period=14, overbought=70, oversold=30, adx_threshold=25):
        self.market_state = market_state
        self.market_data = market_data
        self.volatility_analyzer = volatility_analyzer
        self.period = period
        self.base_overbought = overbought
        self.base_oversold = oversold
        self.overbought = overbought
        self.oversold = oversold
        self.adx_threshold = adx_threshold

    async def adapt_parameters(self, symbol, timeframe, limit, exchange_name):
        """Adapt RSI thresholds based on market volatility."""
        try:
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines for {symbol}, using default RSI thresholds")
                return
            volatility_factor = self.volatility_analyzer.analyze(klines)
            self.overbought = self.base_overbought + 5 * volatility_factor
            self.oversold = self.base_oversold - 5 * volatility_factor
            logger.info(f"Adapted RSI thresholds for {symbol}: overbought={self.overbought}, oversold={self.oversold}")
        except Exception as e:
            logger.error(f"Failed to adapt parameters for {symbol}: {str(e)}")

    def calculate_rsi(self, closes):
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[:self.period]) if len(gains) >= self.period else 0
        avg_loss = np.mean(losses[:self.period]) if len(losses) >= self.period else 0
        for i in range(self.period, len(deltas)):
            avg_gain = (avg_gain * (self.period - 1) + gains[i]) / self.period
            avg_loss = (avg_loss * (self.period - 1) + losses[i]) / self.period
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        return 100 - (100 / (1 + rs))

    def calculate_adx(self, klines):
        highs = [kline[2] for kline in klines][-self.period:]
        lows = [kline[3] for kline in klines][-self.period:]
        if len(highs) < self.period:
            return 0
        tr = [max(highs[i] - lows[i], abs(highs[i] - closes[i-1]), abs(lows[i] - closes[i-1])) for i in range(1, len(highs))]
        return np.mean(tr) if tr else 0

    async def generate_signal(self, symbol, klines, timeframe, limit, exchange_name):
        """Generate a signal using RSI."""
        try:
            await self.adapt_parameters(symbol, timeframe, limit, exchange_name)
            closes = [kline[4] for kline in klines][-self.period*2:]
            if len(closes) < self.period:
                logger.warning(f"Not enough data for {symbol}")
                return None

            rsi = self.calculate_rsi(closes)
            adx = self.calculate_adx(klines)

            if rsi > self.overbought and adx > self.adx_threshold:
                signal = "sell"
            elif rsi < self.oversold and adx > self.adx_threshold:
                signal = "buy"
            else:
                signal = "hold"

            logger.info(f"RSI signal for {symbol}: {signal}, RSI={rsi}, ADX={adx}, overbought={self.overbought}, oversold={self.oversold}, adx_threshold={self.adx_threshold}")
            return {"symbol": symbol, "strategy": "rsi", "signal": signal, "entry_price": closes[-1], "trade_size": 100, "timeframe": timeframe, "limit": limit, "exchange_name": exchange_name}
        except Exception as e:
            logger.error(f"Failed to generate RSI signal for {symbol}: {str(e)}")
            return None
