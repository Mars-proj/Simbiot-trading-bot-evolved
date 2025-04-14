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

    def calculate_technical_indicators(self, klines: list):
        """Calculate technical indicators (RSI, MACD, Bollinger Bands, ATR, ADX) as features."""
        if len(klines) < 40:  # Минимальное количество свечей для расчётов
            return None

        closes = np.array([kline['close'] for kline in klines])
        highs = np.array([kline['high'] for kline in klines])
        lows = np.array([kline['low'] for kline in klines])

        # RSI (период 14)
        deltas = np.diff(closes)
        gains = np.where(deltas > 0, deltas, 0)
        losses = np.where(deltas < 0, -deltas, 0)
        avg_gain = np.mean(gains[-14:])
        avg_loss = np.mean(losses[-14:])
        rs = avg_gain / avg_loss if avg_loss != 0 else 0
        rsi = 100 - (100 / (1 + rs)) if avg_loss != 0 else 50.0

        # MACD (12, 26, 9)
        def ema(data, period):
            alpha = 2 / (period + 1)
            ema_values = [data[0]]
            for i in range(1, len(data)):
                ema_values.append(alpha * data[i] + (1 - alpha) * ema_values[-1])
            return np.array(ema_values)

        ema_fast = ema(closes, 12)
        ema_slow = ema(closes, 26)
        macd = ema_fast - ema_slow
        signal = ema(macd[-10:], 9)
        macd_line = macd[-1]
        signal_line = signal[-1]
        histogram = macd_line - signal_line

        # Bollinger Bands (период 20, отклонение 2)
        period = 20
        sma = np.mean(closes[-period:])
        std = np.std(closes[-period:])
        upper_band = sma + 2 * std
        lower_band = sma - 2 * std
        bb_width = (upper_band - lower_band) / sma

        # ATR (период 14)
        tr_values = []
        for i in range(1, len(klines)):
            high = klines[i]['high']
            low = klines[i]['low']
            prev_close = klines[i-1]['close']
            tr = max(high - low, abs(high - prev_close), abs(low - prev_close))
            tr_values.append(tr)
        atr = np.mean(tr_values[-14:]) if len(tr_values) >= 14 else 0.0

        # ADX (период 14)
        plus_dm = []
        minus_dm = []
        for i in range(1, len(klines)):
            up_move = klines[i]['high'] - klines[i-1]['high']
            down_move = klines[i-1]['low'] - klines[i]['low']
            plus = up_move if up_move > down_move and up_move > 0 else 0
            minus = down_move if down_move > up_move and down_move > 0 else 0
            plus_dm.append(plus)
            minus_dm.append(minus)
        atr_14 = np.mean(tr_values[-14:]) if len(tr_values) >= 14 else 0.0
        plus_di = 100 * np.mean(plus_dm[-14:]) / atr_14 if atr_14 != 0 else 0
        minus_di = 100 * np.mean(minus_dm[-14:]) / atr_14 if atr_14 != 0 else 0
        adx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di) if (plus_di + minus_di) != 0 else 0

        # Собираем фичи
        features = [
            klines[-1]['open'], klines[-1]['high'], klines[-1]['low'], klines[-1]['close'], klines[-1]['volume'],
            rsi, macd_line, signal_line, histogram, bb_width, atr, adx
        ]
        return features

    async def select_model(self, symbol: str, timeframe: str, limit: int, exchange_name: str) -> str:
        """Select the best model based on market conditions (volatility)."""
        try:
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

            # Формируем фичи с техническими индикаторами
            features_list = []
            for i in range(len(klines) - 1):
                features = self.calculate_technical_indicators(klines[:i+1])
                if features:
                    features_list.append(features)

            if not features_list:
                logger.warning(f"No features generated for {symbol}, skipping retraining")
                return

            data = np.array(features_list)
            labels = np.array([1 if klines[i+1]['close'] > klines[i]['close'] else 0 for i in range(len(klines)-1)])

            try:
                model.train(data, labels)
                logger.info(f"Model {self.current_model} retrained successfully with {len(data)} data points for {symbol}")
            except Exception as e:
                logger.error(f"Failed to retrain {self.current_model} for {symbol}: {str(e)}")
        except Exception as e:
            logger.error(f"Failed to retrain models for {symbol}: {str(e)}")
            return

    async def predict(self, symbol: str, timeframe: str, limit: int, exchange_name: str) -> list:
        """Make predictions using the selected model with advanced features."""
        try:
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

            features = self.calculate_technical_indicators(klines)
            if not features:
                logger.warning(f"No features generated for {symbol}, cannot predict")
                return []

            data = np.array([features])
            predictions = model.predict(data)
            logger.info(f"Predictions made with {self.current_model} for {symbol}: {predictions}")
            return predictions.tolist()
        except Exception as e:
            logger.error(f"Failed to predict for {symbol} with {self.current_model}: {str(e)}")
            return []
