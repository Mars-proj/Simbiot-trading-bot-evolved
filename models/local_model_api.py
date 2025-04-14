import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import numpy as np
import xgboost as xgb
from utils.logging_setup import setup_logging

logger = setup_logging('local_model_api')

class LocalModelAPI:
    def __init__(self, max_depth=6, n_estimators=100):
        """Initialize the XGBoost model."""
        self.max_depth = max_depth
        self.n_estimators = n_estimators
        self.model = xgb.XGBRegressor(max_depth=self.max_depth, n_estimators=self.n_estimators)

    def preprocess_data(self, klines):
        """Preprocess klines data for XGBoost."""
        try:
            if len(klines) < 2:
                logger.warning("Not enough klines data for XGBoost preprocessing")
                return None, None

            features = []
            targets = []
            for i in range(len(klines) - 1):
                kline = klines[i]
                feature = [
                    kline[1],  # Open
                    kline[2],  # High
                    kline[3],  # Low
                    kline[4],  # Close
                    kline[5]   # Volume
                ]
                features.append(feature)
                targets.append(klines[i + 1][4])  # Next closing price
            X = np.array(features)
            y = np.array(targets)
            logger.info(f"Preprocessed {len(X)} samples for XGBoost")
            return X, y
        except Exception as e:
            logger.error(f"Failed to preprocess data for XGBoost: {str(e)}")
            return None, None

    def train(self, klines):
        """Train the XGBoost model."""
        try:
            X, y = self.preprocess_data(klines)
            if X is None or y is None:
                return False
            self.model.fit(X, y)
            logger.info("XGBoost model trained successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to train XGBoost model: {str(e)}")
            return False

    def predict(self, klines):
        """Predict the next price using the XGBoost model."""
        try:
            X, _ = self.preprocess_data(klines)
            if X is None:
                return None
            prediction = self.model.predict(X[-1].reshape(1, -1))
            logger.info(f"XGBoost prediction: {prediction[0]}")
            return prediction[0]
        except Exception as e:
            logger.error(f"Failed to predict with XGBoost model: {str(e)}")
            return None
