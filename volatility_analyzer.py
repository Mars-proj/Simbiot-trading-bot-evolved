import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
from utils.logging_setup import setup_logging
from arch import arch_model

logger = setup_logging('volatility_analyzer')

class VolatilityAnalyzer:
    def __init__(self, market_state: dict, market_data):
        self.market_state = market_state
        self.market_data = market_data
        self.volatility = market_state.get('volatility', 0.3)

    async def analyze_volatility(self, symbol: str, timeframe: str, limit: int, exchange_name: str) -> float:
        """Analyze the volatility of a symbol using GARCH(1,1) model."""
        try:
            supported_timeframes = await self.market_data.get_supported_timeframes(exchange_name, symbol)
            if not supported_timeframes:
                logger.error(f"No supported timeframes for {exchange_name}, using default '1m'")
                timeframe = '1m'
            elif timeframe not in supported_timeframes:
                logger.warning(f"Timeframe {timeframe} not supported on {exchange_name}, using {supported_timeframes[0]}")
                timeframe = supported_timeframes[0]

            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines data for {symbol} on {exchange_name}, returning default volatility")
                return self.volatility

            prices = [kline['close'] for kline in klines]
            if not prices or min(prices) == 0:
                logger.warning(f"Invalid price data for {symbol}, returning default volatility")
                return self.volatility

            # Рассчитываем логарифмические доходности
            returns = np.diff(np.log(prices)) * 100  # В процентах
            if len(returns) < 10:
                logger.warning(f"Not enough returns data for {symbol}, returning default volatility")
                return self.volatility

            # Применяем GARCH(1,1) модель
            model = arch_model(returns, vol='Garch', p=1, q=1, mean='Zero', rescale=False)
            res = model.fit(disp='off')
            conditional_volatility = res.conditional_volatility[-1]  # Последняя оценка волатильности
            annualized_volatility = conditional_volatility * np.sqrt(365 * 24 * 60)  # Аннуализируем

            volatility = annualized_volatility / 100  # Переводим в доли
            logger.info(f"GARCH volatility for {symbol} on {exchange_name}: {volatility}")
            return volatility
        except Exception as e:
            logger.error(f"Failed to analyze volatility for {symbol}: {str(e)}")
            return self.volatility
