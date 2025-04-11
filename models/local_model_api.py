from trading_bot.logging_setup import setup_logging
from .lstm_model import LSTMModel
from .rnn_model import RNNModel
from .transformer_model import TransformerModel
from .xgboost_model import XGBoostModel

logger = setup_logging('local_model_api')

class LocalModelAPI:
    def __init__(self, market_state: dict, model_type: str = 'lstm'):
        self.volatility = market_state['volatility']
        self.model_type = model_type
        self.model = self._initialize_model(market_state)

    def _initialize_model(self, market_state):
        """Initialize the specified model."""
        try:
            if self.model_type == 'lstm':
                model = LSTMModel(market_state)
            elif self.model_type == 'rnn':
                model = RNNModel(market_state)
            elif self.model_type == 'transformer':
                model = TransformerModel(market_state)
            elif self.model_type == 'xgboost':
                model = XGBoostModel(market_state)
            else:
                raise ValueError(f"Unsupported model type: {self.model_type}")
            
            logger.info(f"Initialized {self.model_type} model")
            return model
        except Exception as e:
            logger.error(f"Failed to initialize model: {str(e)}")
            raise

    def train(self, X, y):
        """Train the model."""
        try:
            self.model.train(X, y)
            logger.info(f"Trained {self.model_type} model")
        except Exception as e:
            logger.error(f"Failed to train {self.model_type} model: {str(e)}")
            raise

    def predict(self, X):
        """Make predictions using the model."""
        try:
            predictions = self.model.predict(X)
            logger.info(f"Made predictions with {self.model_type} model")
            return predictions
        except Exception as e:
            logger.error(f"Failed to make predictions with {self.model_type} model: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    api = LocalModelAPI(market_state, model_type='lstm')
    X = np.array([[50000 + i * 100] for i in range(10)])
    y = np.array([51000 + i * 100 for i in range(10)])
    api.train(X, y)
    predictions = api.predict(X)
    print(f"Predictions: {predictions}")
