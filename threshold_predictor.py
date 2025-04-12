from trading_bot.logging_setup import setup_logging
from trading_bot.models.local_model_api import LocalModelAPI

logger = setup_logging('threshold_predictor')

class ThresholdPredictor:
    def __init__(self, market_state: dict, model_type: str = 'xgboost'):
        self.volatility = market_state['volatility']
        self.model_api = LocalModelAPI(market_state, model_type)

    def train(self, X, y):
        """Train the threshold prediction model."""
        try:
            # Динамическая корректировка данных на основе волатильности
            X_adjusted = [x * (1 + self.volatility / 2) for x in X]
            y_adjusted = [y_val * (1 + self.volatility / 2) for y_val in y]
            
            self.model_api.train(X_adjusted, y_adjusted)
            logger.info("Threshold predictor trained successfully")
        except Exception as e:
            logger.error(f"Failed to train threshold predictor: {str(e)}")
            raise

    def predict(self, X):
        """Predict thresholds using the trained model."""
        try:
            # Динамическая корректировка данных на основе волатильности
            X_adjusted = [x * (1 + self.volatility / 2) for x in X]
            
            predictions = self.model_api.predict(X_adjusted)
            logger.info(f"Threshold predictions: {predictions}")
            return predictions
        except Exception as e:
            logger.error(f"Failed to predict thresholds: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    import numpy as np
    market_state = {'volatility': 0.3}
    predictor = ThresholdPredictor(market_state)
    X = np.array([[50000 + i * 100] for i in range(10)])
    y = np.array([51000 + i * 100 for i in range(10)])
    predictor.train(X, y)
    predictions = predictor.predict(X)
    print(f"Threshold predictions: {predictions}")
