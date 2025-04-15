from utils.logging_setup import setup_logging

logger = setup_logging('grid_strategy')

class GridStrategy:
    def __init__(self, market_state, market_data, volatility_analyzer):
        self.market_state = market_state
        self.market_data = market_data
        self.volatility_analyzer = volatility_analyzer
        self.grid_levels = 5
        self.grid_spacing = 0.01

    async def adapt_parameters(self, symbol, timeframe, limit, exchange_name):
        """Adapt grid spacing based on volatility."""
        try:
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines for {symbol}, using default grid spacing")
                return
            volatility_factor = self.volatility_analyzer.analyze(klines)
            self.grid_spacing = 0.01 * (1 + volatility_factor)
            logger.info(f"Adapted grid spacing for {symbol}: {self.grid_spacing}")
        except Exception as e:
            logger.error(f"Failed to adapt parameters for {symbol}: {str(e)}")

    async def generate_signal(self, symbol, klines, timeframe, limit, exchange_name):
        """Generate a grid trading signal (simplified)."""
        try:
            await self.adapt_parameters(symbol, timeframe, limit, exchange_name)
            current_price = klines[-1][4]
            base_price = klines[-self.grid_levels][4] if len(klines) >= self.grid_levels else current_price
            price_diff = (current_price - base_price) / base_price if base_price != 0 else 0

            if price_diff > self.grid_spacing * self.grid_levels:
                signal = "sell"
            elif price_diff < -self.grid_spacing * self.grid_levels:
                signal = "buy"
            else:
                signal = "hold"

            logger.info(f"Generated grid signal for {symbol}: {signal}")
            return {"symbol": symbol, "strategy": "grid", "signal": signal, "entry_price": current_price, "trade_size": 100, "timeframe": timeframe, "limit": limit, "exchange_name": exchange_name}
        except Exception as e:
            logger.error(f"Failed to generate grid signal for {symbol}: {str(e)}")
            return None
