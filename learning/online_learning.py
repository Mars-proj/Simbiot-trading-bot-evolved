import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import numpy as np
import time
from models.local_model_api import LocalModelAPI
from models.transformer_model import TransformerModel
from models.lstm_model import LSTMModel
from models.rnn_model import RNNModel
from utils.logging_setup import setup_logging

logger = setup_logging('online_learning')

class OnlineLearning:
    def __init__(self, market_state, market_data):
        """Initialize the Online Learning module."""
        logger.info("Starting initialization of OnlineLearning")
        self.market_state = market_state
        self.market_data = market_data
        self.models = {}
        self.models['xgboost'] = LocalModelAPI()
        logger.info("XGBoost model initialized")
        self.models['transformer'] = TransformerModel()
        logger.info("Transformer model initialized")
        self.models['lstm'] = LSTMModel()
        logger.info("LSTM model initialized")
        self.models['rnn'] = RNNModel()
        logger.info("RNN model initialized")
        self.performance_metrics = {}  # Track performance of each model
        self.retrain_interval = 300  # Retrain every 5 minutes
        self.last_retrain = {}
        logger.info("Finished initialization of OnlineLearning")

    async def retrain(self, symbol: str, timeframe: str, limit: int, exchange_name: str):
        """Retrain all models for a symbol asynchronously."""
        try:
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines data for {symbol}, skipping retraining")
                return

            for model_name, model in self.models.items():
                if model_name not in self.last_retrain or (time.time() - self.last_retrain.get(model_name, 0)) > self.retrain_interval:
                    success = model.train(klines)
                    if success:
                        self.last_retrain[model_name] = time.time()
                        logger.info(f"Retrained {model_name} model for {symbol}")
                    else:
                        logger.warning(f"Failed to retrain {model_name} model for {symbol}")
        except Exception as e:
            logger.error(f"Failed to retrain models for {symbol}: {str(e)}")

    async def predict(self, symbol: str, timeframe: str, limit: int, exchange_name: str):
        """Predict the next price using the best model asynchronously."""
        try:
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No klines data for {symbol}, skipping prediction")
                return None

            predictions = {}
            for model_name, model in self.models.items():
                prediction = model.predict(klines)
                if prediction is not None:
                    predictions[model_name] = prediction
                    logger.info(f"{model_name} predicted {prediction} for {symbol}")

            if not predictions:
                logger.warning(f"No predictions available for {symbol}")
                return None

            best_model = max(self.performance_metrics, key=lambda x: self.performance_metrics.get(x, 0), default='xgboost')
            prediction = predictions.get(best_model, list(predictions.values())[0])
            logger.info(f"Selected {best_model} for prediction: {prediction}")

            for model_name, pred in predictions.items():
                self.performance_metrics[model_name] = self.performance_metrics.get(model_name, 0) + (1 if pred == prediction else 0)

            return prediction
        except Exception as e:
            logger.error(f"Failed to predict for {symbol}: {str(e)}")
            return None

    async def select_model(self, volatility: float):
        """Select the best model based on market volatility asynchronously."""
        try:
            if volatility > 0.5:
                return 'transformer' if self.performance_metrics.get('transformer', 0) > self.performance_metrics.get('lstm', 0) else 'lstm'
            elif volatility > 0.2:
                return 'rnn'
            else:
                return 'xgboost'
        except Exception as e:
            logger.error(f"Failed to select model: {str(e)}")
            return 'xgboost'
