from utils.logging_setup import setup_logging

logger = setup_logging('ml_strategy')

class MLStrategy:
    def __init__(self, market_state, market_data, volatility_analyzer, model):
        self.market_state = market_state
        self.market_data = market_data
        self.volatility_analyzer = volatility_analyzer
        self.model = model

    def generate_signal(self, symbol, klines, timeframe, limit, exchange_name):
        """Generate a signal using ML model."""
        try:
            prediction = self.model.predict(symbol, timeframe, limit, exchange_name)
            if prediction is None:
                logger.warning(f"No prediction for {symbol}")
                return None

            signal = "buy" if prediction > 0 else "sell" if prediction < 0 else "hold"
            logger.info(f"ML signal for {symbol}: {signal}, prediction={prediction}")
            return {"symbol": symbol, "strategy": "ml", "signal": signal, "entry_price": klines[-1][4], "trade_size": 100, "timeframe": timeframe, "limit": limit, "exchange_name": exchange_name}
        except Exception as e:
            logger.error(f"Failed to generate ML signal for {symbol}: {str(e)}")
            return None
