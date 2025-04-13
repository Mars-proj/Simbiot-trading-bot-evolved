import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import numpy as np
from utils.logging_setup import setup_logging
from models.local_model_api import LocalModelAPI
from models.transformer_model import TransformerModel
from volatility_analyzer import VolatilityAnalyzer

logger = setup_logging('online_learning')

class OnlineLearning:
    def __init__(self, market_state: dict, market_data):
        self.market_state = market_state
        self.market_data = market_data
        self.volatility_analyzer = VolatilityAnalyzer(market_state, market_data)
        self.models = {
            'xgboost': LocalModelAPI(market_state),
            'transformer': TransformerModel(),
        }
        self.current_model = 'xgboost'

    async def select_model(self, symbol: str, timeframe: str, limit: int, exchange_name: str) -> str:
        """Select the best model based on market conditions (volatility)."""
        try:
            # Адаптируем timeframe
            supported_timeframes = await self.market_data.get_supported_timeframes(exchange_name, symbol)
            if not supported_timeframes:
                logger.error(f"No supported timeframes for {exchange_name}, using default '1m'")
                timeframe = '1m'
            elif timeframe not in supported_timeframes:
                logger.warning(f"Timeframe {timeframe} not supported on {exchange_name}, using {supported_timeframes[0]}")
                timeframe = supported_timeframes[0]

            volatility = await self.volatility_analyzer.analyze_volatility(symbol, timeframe, limit, exchange_name)
            if volatility > 0.5:
                self.current_model = 'transformer'
                logger.info(f"Selected transformer model for {symbol} due to high volatility: {volatility}")
            else:
                self.current_model = 'xgboost'
                logger.info(f"Selected xgboost model for {symbol} due to low volatility: {volatility}")
            return self.current_model
        except Exception as e:
            logger.error(f"Failed to select model for {symbol}, using default: {self.current_model}. Error: {str(e)}")
            return self.current_model

    async def retrain(self, symbol: str, timeframe: str, limit: int, exchange_name: str):
        """Retrain the selected model with new data for a single symbol."""
        try:
            # Адаптируем timeframe
            supported_timeframes = await self.market_data.get_supported_timeframes(exchange_name, symbol)
            if not supported_timeframes:
                logger.error(f"No supported timeframes for {exchange_name}, using default '1m'")
                timeframe = '1m'
            elif timeframe not in supported_timeframes:
                logger.warning(f"Timeframe {timeframe} not supported on {exchange_name}, using {supported_timeframes[0]}")
                timeframe = supported_timeframes[0]

            await self.select_model(symbol, timeframe, limit, exchange_name)
            model = self.models[self.current_model]

            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines data for {symbol}, skipping retraining")
                return

            data = np.array([[kline['open'], kline['high'], kline['low'], kline['close'], kline['volume']] for kline in klines])
            labels = np.array([1 if kline['close'] > kline['open'] else 0 for kline in klines])

            try:
                model.train(data, labels)
                logger.info(f"Model {self.current_model} retrained successfully with {len(data)} data points for {symbol}")
            except Exception as e:
                logger.error(f"Failed to retrain {self.current_model} for {symbol}: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to retrain models for {symbol}: {str(e)}")
            return

    async def predict(self, symbol: str, timeframe: str, limit: int, exchange_name: str) -> list:
        """Make predictions using the selected model."""
        try:
            # Адаптируем timeframe
            supported_timeframes = await self.market_data.get_supported_timeframes(exchange_name, symbol)
            if not supported_timeframes:
                logger.error(f"No supported timeframes for {exchange_name}, using default '1m'")
                timeframe = '1m'
            elif timeframe not in supported_timeframes:
                logger.warning(f"Timeframe {timeframe} not supported on {exchange_name}, using {supported_timeframes[0]}")
                timeframe = supported_timeframes[0]

            await self.select_model(symbol, timeframe, limit, exchange_name)
            model = self.models[self.current_model]

            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines data for {symbol}, cannot predict")
                return []

            data = np.array([[kline['open'], kline['high'], kline['low'], kline['close'], kline['volume']] for kline in klines])
            predictions = model.predict(data)
            logger.info(f"Predictions made with {self.current_model} for {symbol}: {predictions}")
            return predictions
        except Exception as e:
            logger.error(f"Failed to predict for {symbol} with {self.current_model}: {str(e)}")
            return []
