from trading_bot.logging_setup import setup_logging
from .base_model import BaseModel
import numpy as np
import xgboost as xgb

logger = setup_logging('xgboost_model')

class XGBoostModel(BaseModel):
    def __init__(self, market_state: dict, n_estimators: int = 100):
        super().__init__(market_state)
        self.n_estimators = n_estimators
        self.model = xgb.XGBRegressor(n_estimators=self.n_estimators)

    def train(self, X, y):
        """Train the XGBoost model."""
        try:
            # Корректируем данные на основе волатильности
            X_adjusted = self.adjust_data(X)
            y_adjusted = self.adjust_data(y)
            
            self.model.fit(X_adjusted, y_adjusted)
            logger.info("XGBoost model trained successfully")
        except Exception as e:
            logger.error(f"Failed to train XGBoost model: {str(e)}")
            raise

    def predict(self, X):
        """Make predictions using the XGBoost model."""
        try:
            # Корректируем данные на основе волатильности
            X_adjusted = self.adjust_data(X)
            
            predictions = self.model.predict(X_adjusted)
            logger.info(f"Made {len(predictions)} predictions with XGBoost model")
            return predictions
        except Exception as e:
            logger.error(f"Failed to make predictions with XGBoost model: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    model = XGBoostModel(market_state)
    X = np.array([[50000 + i * 100] for i in range(10)])
    y = np.array([51000 + i * 100 for i in range(10)])
    model.train(X, y)
    predictions = model.predict(X)
    print(f"Predictions: {predictions}")
