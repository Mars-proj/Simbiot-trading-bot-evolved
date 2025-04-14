import numpy as np
from utils.logging_setup import setup_logging

logger = setup_logging('bollinger_strategy')

class BollingerStrategy:
    def __init__(self, market_state, market_data, volatility_analyzer, period=20, deviation=2):
        self.market_state = market_state
        self.market_data = market_data
        self.volatility_analyzer = volatility_analyzer
        self.period = period
        self.base_deviation = deviation
        self.deviation = deviation  # Будет адаптироваться

    def adapt_parameters(self, symbol, timeframe, limit, exchange_name):
        """Adapt Bollinger Bands deviation based on market volatility."""
        try:
            klines = self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines for {symbol}, using default deviation")
                return
            # Пример адаптации: увеличиваем deviation при высокой волатильности
            self.deviation = self.base_deviation * (1 + self.volatility_analyzer.analyze(klines))
            logger.info(f"Adapted deviation for {symbol}: {self.deviation}")
        except Exception as e:
            logger.error(f"Failed to adapt parameters for {symbol}: {str(e)}")

    def generate_signal(self, symbol, klines, timeframe, limit, exchange_name):
        """Generate a signal using Bollinger Bands."""
        try:
            self.adapt_parameters(symbol, timeframe, limit, exchange_name)
            closes = [kline[4] for kline in klines][-self.period:]  # Последние period закрытий
            if len(closes) < self.period:
                logger.warning(f"Not enough data for {symbol}")
                return None

            sma = np.mean(closes)
            std = np.std(closes)
            upper_band = sma + self.deviation * std
            lower_band = sma - self.deviation * std
            current_price = closes[-1]

            if current_price > upper_band:
                signal = "sell"
            elif current_price < lower_band:
                signal = "buy"
            else:
                signal = "hold"

            logger.info(f"Generated Bollinger signal for {symbol}: {signal}, upper={upper_band}, lower={lower_band}, price={current_price}")
            return {"symbol": symbol, "strategy": "bollinger", "signal": signal, "entry_price": current_price, "trade_size": 100, "timeframe": timeframe, "limit": limit, "exchange_name": exchange_name}
        except Exception as e:
            logger.error(f"Failed to generate Bollinger signal for {symbol}: {str(e)}")
            return None
