from utils.logging_setup import setup_logging

logger = setup_logging('signal_generator')

class SignalGenerator:
    def __init__(self, market_state, market_data, volatility_analyzer):
        self.market_state = market_state
        self.market_data = market_data
        self.volatility_analyzer = volatility_analyzer

    def generate(self, symbol, klines, timeframe, limit, exchange_name):
        """Generate a signal based on volatility and price movement."""
        try:
            volatility = self.volatility_analyzer.analyze(klines)
            closes = [kline[4] for kline in klines][-2:]  # Последние две цены
            if len(closes) < 2:
                logger.warning(f"Not enough data for {symbol}")
                return None

            price_change = (closes[-1] - closes[-2]) / closes[-2] if closes[-2] != 0 else 0
            if volatility > 0.05 and price_change > 0.01:
                signal = "sell"
            elif volatility < 0.05 and price_change < -0.01:
                signal = "buy"
            else:
                signal = "hold"

            logger.info(f"Generated signal for {symbol}: {signal}, volatility={volatility}, price_change={price_change}")
            return {"symbol": symbol, "strategy": "signal_generator", "signal": signal, "entry_price": closes[-1], "trade_size": 100, "timeframe": timeframe, "limit": limit, "exchange_name": exchange_name}
        except Exception as e:
            logger.error(f"Failed to generate signal for {symbol}: {str(e)}")
            return None
