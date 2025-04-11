from trading_bot.logging_setup import setup_logging
from trading_bot.analysis.ml_predictor import MLPredictor

logger = setup_logging('ml_strategy')

class MLStrategy:
    def __init__(self, market_state: dict, model):
        self.volatility = market_state['volatility']
        self.predictor = MLPredictor(model, market_state)

    def generate_signals(self, X: np.ndarray) -> list:
        """Generate trading signals using ML predictions."""
        try:
            if X.shape[0] == 0:
                logger.warning("No data provided for ML strategy")
                return []

            # Получаем предсказания
            predictions = self.predictor.predict(X)
            
            signals = []
            for i in range(len(predictions)):
                predicted_price = predictions[i]
                current_price = X[i][-1]  # Последняя цена в окне
                
                # Динамический порог на основе волатильности
                threshold = 0.01 * (1 + self.volatility)
                if predicted_price > current_price * (1 + threshold):
                    signals.append({'timestamp': i, 'signal': 'buy'})
                elif predicted_price < current_price * (1 - threshold):
                    signals.append({'timestamp': i, 'signal': 'sell'})
                else:
                    signals.append({'timestamp': i, 'signal': 'hold'})
            
            logger.info(f"Generated {len(signals)} ML strategy signals")
            return signals
        except Exception as e:
            logger.error(f"Failed to generate ML strategy signals: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    from sklearn.linear_model import LinearRegression
    import numpy as np
    market_state = {'volatility': 0.3}
    model = LinearRegression()
    X_train = np.array([[50000 + i * 100] for i in range(10)])
    y_train = np.array([51000 + i * 100 for i in range(10)])
    model.fit(X_train, y_train)
    strategy = MLStrategy(market_state, model)
    X_test = np.array([[52000], [53000]])
    signals = strategy.generate_signals(X_test)
    print(f"Signals: {signals}")
