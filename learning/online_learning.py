import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from utils.logging_setup import setup_logging
from models.xgboost_model import XGBoostModel
from models.lstm_model import LSTMModel
from models.rnn_model import RNNModel
from models.transformer_model import TransformerModel

logger = setup_logging('online_learning')

class OnlineLearning:
    def __init__(self, market_state: dict, market_data):
        self.market_state = market_state
        self.market_data = market_data
        self.models = {
            'xgboost': XGBoostModel(),
            'lstm': LSTMModel(),
            'rnn': RNNModel(),
            'transformer': TransformerModel()
        }
        self.current_model = 'xgboost'  # Модель по умолчанию

    def set_model(self, model_name: str):
        """Set the model to use for online learning."""
        if model_name in self.models:
            self.current_model = model_name
            logger.info(f"Set online learning model to {model_name}")
        else:
            logger.error(f"Model {model_name} not found. Available models: {list(self.models.keys())}")
            raise ValueError(f"Model {model_name} not found")

    async def retrain_model(self, symbols: list, timeframe: str, limit: int, exchange_name: str):
        """Retrain the ML model with new data for all symbols."""
        try:
            logger.info(f"Starting online retraining for {len(symbols)} symbols on {exchange_name}")
            tasks = [self.market_data.get_klines(symbol, timeframe, limit, exchange_name) for symbol in symbols]
            klines_list = await asyncio.gather(*tasks, return_exceptions=True)

            all_features = []
            all_labels = []
            for symbol, klines in zip(symbols, klines_list):
                if isinstance(klines, Exception) or not klines:
                    logger.warning(f"No data for {symbol} to retrain model")
                    continue

                features = self.prepare_features(klines)
                labels = self.prepare_labels(klines)
                all_features.extend(features)
                all_labels.extend(labels)

            if not all_features or not all_labels:
                logger.warning("No data available for retraining")
                return False

            # Переобучение текущей модели
            self.models[self.current_model].update(all_features, all_labels)
            logger.info(f"Model {self.current_model} retrained successfully with {len(all_features)} data points")
            return True
        except Exception as e:
            logger.error(f"Failed to retrain model: {str(e)}")
            return False

    def prepare_features(self, klines: list) -> list:
        """Prepare features for ML model from klines."""
        features = []
        for kline in klines:
            # Извлечение цен закрытия, объёмов, и других метрик
            feature = [
                kline['close'],  # Цена закрытия
                kline['volume'],  # Объём
                (kline['high'] - kline['low']) / kline['close'],  # Волатильность
                kline['close'] - kline['open']  # Дельта цены
            ]
            features.append(feature)
        return features

    def prepare_labels(self, klines: list) -> list:
        """Prepare labels for ML model from klines."""
        labels = []
        for i in range(len(klines) - 1):
            # Метка 1 (рост), если следующая цена выше текущей, иначе 0
            labels.append(1 if klines[i + 1]['close'] > klines[i]['close'] else 0)
        return labels

if __name__ == "__main__":
    # Test run
    import asyncio
    from data_sources.market_data import MarketData
    market_state = {'volatility': 0.3}
    market_data = MarketData(market_state)
    online_learning = OnlineLearning(market_state, market_data)
    
    async def main():
        symbols = ['BTC/USDT', 'ETH/USDT']
        success = await online_learning.retrain_model(symbols, '1h', 100, 'mexc')
        print(f"Retraining successful: {success}")

    asyncio.run(main())
