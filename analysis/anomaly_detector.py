from trading_bot.logging_setup import setup_logging
from trading_bot.utils.utils_utils import calculate_dynamic_threshold

logger = setup_logging('anomaly_detector')

class AnomalyDetector:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']

    def detect_anomalies(self, data: list) -> list:
        """Detect anomalies in market data."""
        try:
            if not data:
                return []

            values = [float(d['close']) for d in data]
            mean = sum(values) / len(values)
            std_dev = (sum((x - mean) ** 2 for x in values) / len(values)) ** 0.5
            
            # Динамический порог на основе волатильности
            threshold = calculate_dynamic_threshold({'volatility': self.volatility}, 2.0)
            anomalies = [d for i, d in enumerate(data) if abs(values[i] - mean) > threshold * std_dev]
            
            logger.info(f"Detected {len(anomalies)} anomalies in market data")
            return anomalies
        except Exception as e:
            logger.error(f"Failed to detect anomalies: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    detector = AnomalyDetector(market_state)
    data = [
        {'close': 50000},
        {'close': 51000},
        {'close': 60000},  # Anomaly
        {'close': 50500}
    ]
    anomalies = detector.detect_anomalies(data)
    print(f"Anomalies: {anomalies}")

