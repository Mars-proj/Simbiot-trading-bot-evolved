import matplotlib.pyplot as plt
from trading_bot.logging_setup import setup_logging
from trading_bot.utils.performance_tracker import PerformanceTracker
from trading_bot.utils.time_utils import TimeUtils

logger = setup_logging('performance_charts')

class PerformanceCharts:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.performance_tracker = PerformanceTracker(market_state)
        self.time_utils = TimeUtils(market_state)

    def plot_metrics(self) -> None:
        """Plot performance metrics with real timestamps."""
        try:
            metrics = self.performance_tracker.get_metrics()
            
            # Получаем временные метки для метрик
            timestamps = []
            requests_per_second = []
            for i in range(5):
                metrics = self.performance_tracker.get_metrics()
                timestamps.append(self.time_utils.get_current_timestamp())
                requests_per_second.append(metrics['requests_per_second'])
                time.sleep(1)  # Задержка для получения разных временных меток
            
            # Форматируем временные метки для отображения
            formatted_timestamps = [self.time_utils.format_timestamp(ts) for ts in timestamps]
            
            plt.figure(figsize=(10, 5))
            plt.plot(formatted_timestamps, requests_per_second, label='Requests per Second')
            plt.xlabel('Time')
            plt.ylabel('Requests per Second')
            plt.title('Performance Metrics Over Time')
            plt.legend()
            plt.grid()
            plt.xticks(rotation=45)
            plt.tight_layout()
            plt.show()
            logger.info("Plotted performance metrics")
        except Exception as e:
            logger.error(f"Failed to plot metrics: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    market_state = {'volatility': 0.3}
    charts = PerformanceCharts(market_state)
    charts.plot_metrics()
