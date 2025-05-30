from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import SimpleRNN, Dense
import numpy as np
from utils.logging_setup import setup_logging

logger = setup_logging('rnn_model')

class RNNModel:
    def __init__(self):
        logger.info("Starting initialization of RNNModel")
        self.model = Sequential([
            SimpleRNN(50, input_shape=(20, 1), return_sequences=True),
            SimpleRNN(50),
            Dense(1)
        ])
        self.model.compile(optimizer='adam', loss='mse')
        logger.info("RNN model built successfully")

    def train(self, klines):
        try:
            closes = [kline[4] for kline in klines][-200:]
            if len(closes) < 40:
                logger.warning("Not enough data for training RNN")
                return False
            data = np.array(closes)
            X, y = [], []
            for i in range(len(data) - 20):
                X.append(data[i:i+20])
                y.append(data[i+20])
            X = np.array(X).reshape(-1, 20, 1)
            y = np.array(y)
            self.model.fit(X, y, epochs=1, verbose=0)
            logger.info("RNN model trained successfully")
            return True
        except Exception as e:
            logger.error(f"Failed to train RNN model: {str(e)}")
            return False

    def predict(self, klines):
        try:
            closes = [kline[4] for kline in klines][-20:]
            if len(closes) < 20:
                logger.warning("Not enough data for prediction")
                return None
            X = np.array(closes).reshape(1, 20, 1)
            prediction = self.model.predict(X, verbose=0)[0][0]
            logger.info(f"RNN prediction: {prediction}")
            return prediction
        except Exception as e:
            logger.error(f"Failed to predict with RNN model: {str(e)}")
            return None
