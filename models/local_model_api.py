from trading_bot.logging_setup import setup_logging
from trading_bot.data_sources.market_data import MarketData
from .base_model import BaseModel
from .lstm_model import LSTMModel
from .xgboost_model import XGBoostModel
from .rnn_model import RNNModel
from .transformer_model import TransformerModel

logger = setup_logging('local_model_api')

class LocalModelAPI:
    def __init__(self, market_state: dict, model_type: str = 'xgboost'):
        self.volatility = market_state['volatility']
        self.market_data = MarketData(market_state)
        if model_type == 'lstm':
            self.model = LSTMModel(market_state)
        elif model_type == 'xgboost':
            self.model = XGBoostModel(market_state)
        elif model_type == 'rnn':
            self.model = RNNModel(market_state)
        elif model_type == 'transformer':
            self.model = TransformerModel(market_state)
        else:
            raise ValueError(f"Unsupported model type: {model_type}")

    def train(self, X: list, y: list) -> None:
        """Train the selected model."""
        try:
            logger.info(f"Training {type(self.model).__name__} model...")
            self.model.train(X, y)
            logger.info(f"{type(self.model).__name__} model trained successfully")
        except Exception as e:
            logger.error(f"Failed to train {type(self.model).__name__} model: {str(e)}")
            raise

    def predict(self, X: list) -> list:
        """Make predictions using the selected model."""
        try:
            logger.info(f"Making predictions with {type(self.model).__name__} model...")
            predictions = self.model.predict(X)
            logger.info(f"Predictions made: {predictions[:5]}...")
            return predictions
        except Exception as e:
            logger.error(f"Failed to make predictions with {type(self.model).__name__} model: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    from trading_bot.symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    api = LocalModelAPI(market_state, 'xgboost')
    symbol_filter = SymbolFilter(market_state)
    
    # Получаем символы
    symbols = symbol_filter.filter_symbols(api.market_data.get_symbols('binance'), 'binance')
    
    if symbols:
        # Получаем данные для обучения
        klines = api.market_data.get_klines(symbols[0], '1h', 50, 'binance')
        X = [kline['close'] for kline in klines[:-1]]  # Цены закрытия для обучения
        y = [kline['close'] for kline in klines[1:]]   # Следующие цены закрытия как целевые значения
        
        api.train(X, y)
        predictions = api.predict(X)
        print(f"Predictions for {symbols[0]}: {predictions}")
    else:
        print("No symbols available for testing")
