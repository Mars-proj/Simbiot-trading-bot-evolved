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
        self.market_index_symbol = 'BTCUSDT'

    async def fetch_market_index_data(self, timeframe: str, limit: int, exchange_name: str):
        """Fetch market index data (e.g., BTCUSDT)."""
        klines = await self.market_data.get_klines(self.market_index_symbol, timeframe, limit, exchange_name)
        if not klines:
            logger.warning(f"No market index data for {self.market_index_symbol}")
            return None
        return klines

    def calculate_correlation(self, prices1: list, prices2: list):
        """Calculate Pearson correlation between two price series."""
        if len(prices1) != len(prices2) or len(prices1) < 2:
            return 0.0
        prices1 = np.array(prices1)
        prices2 = np.array(prices2)
        return np.corrcoef(prices1, prices2)[0, 1]

    def calculate_obv(self, klines: list):
        """Calculate On-Balance Volume (OBV)."""
        if len(klines) < 2:
            return 0.0
        obv = 0
        for i in range(1, len(klines)):
            if klines[i]['close'] > klines[i-1]['close']:
                obv += klines[i]['volume']
            elif klines[i]['close'] < klines[i-1]['close']:
                obv -= klines[i]['volume']
        return obv

    async def calculate_technical_indicators(self, klines: list, market_klines: list = None, timeframe: str = None, limit: int = None, exchange_name: str = None):
        """Calculate technical indicators (RSI, MACD, Bollinger Bands, ATR, ADX, OBV, correlations) as features."""
        if len(klines) < 40:
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
        if plus_di + minus_di == 0:
            adx = 0
        else:
            adx = 100 * abs(plus_di - minus_di) / (plus_di + minus_di)

        # OBV
        obv = self.calculate_obv(klines)

        # Корреляция с рыночным индексом
        market_correlation = 0.0
        if market_klines and len(market_klines) == len(klines):
            market_closes = [kline['close'] for kline in market_klines]
            market_correlation = self.calculate_correlation(closes, market_closes)

        # Корреляция с другими символами
        sample_symbols = ['ETHUSDT', 'BNBUSDT', 'XRPUSDT']
        correlations = []
        for sym in sample_symbols:
            sym_klines = await self.market_data.get_klines(sym, timeframe, limit, exchange_name)
            if sym_klines and len(sym_klines) == len(klines):
                sym_closes = [kline['close'] for kline in sym_klines]
                corr = self.calculate_correlation(closes, sym_closes)
                correlations.append(corr)
            else:
                correlations.append(0.0)
        avg_correlation = np.mean(correlations) if correlations else 0.0

        features = [
            klines[-1]['open'], klines[-1]['high'], klines[-1]['low'], klines[-1]['close'], klines[-1]['volume'],
            rsi, macd_line, signal_line, histogram, bb_width, atr, adx,
            obv, market_correlation, avg_correlation
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

            market_klines = await self.fetch_market_index_data(timeframe, limit, exchange_name)

            features_list = []
            for i in range(len(klines) - 1):
                features = await self.calculate_technical_indicators(
                    klines[:i+1], 
                    market_klines[:i+1] if market_klines else None,
                    timeframe,
                    limit,
                    exchange_name
                )
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

            market_klines = await self.fetch_market_index_data(timeframe, limit, exchange_name)

            features = await self.calculate_technical_indicators(klines, market_klines, timeframe, limit, exchange_name)
            if not features:
                logger.warning(f"No features generated for {symbol}, cannot predict")
                return []

            data = np.array([features])
            predictions = model.predict(data)
            logger.info(f"Predictions made with {self.current_model} for {symbol}: {predictions}")
            if isinstance(predictions, np.ndarray):
                return predictions.tolist()
            elif isinstance(predictions, list):
                return predictions
            else:
                return [predictions]
        except Exception as e:
            logger.error(f"Failed to predict for {symbol} with {self.current_model}: {str(e)}")
            return []
