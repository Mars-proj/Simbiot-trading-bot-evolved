import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from utils.logging_setup import setup_logging
from models.local_model_api import LocalModelAPI

logger = setup_logging('ml_trainer')

class MLTrainer:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.model = LocalModelAPI(market_state, 'xgboost')

    def train_model(self, features: list, labels: list) -> None:
        """Train the machine learning model with the provided features and labels."""
        try:
            self.model.train(features, labels)
            logger.info("Model training completed")
        except Exception as e:
            logger.error(f"Failed to train model: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    trainer = MLTrainer(market_state)
    
    # Симулируем данные для обучения
    features = [[1, 2, 3], [4, 5, 6], [7, 8, 9]]
    labels = [0, 1, 0]
    trainer.train_model(features, labels)
