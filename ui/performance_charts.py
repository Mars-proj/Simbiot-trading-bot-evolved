import matplotlib.pyplot as plt
from trading_bot.logging_setup import setup_logging
from trading_bot.utils.performance_tracker import PerformanceTracker

logger = setup_logging('performance_charts')

class PerformanceCharts:
    def __init__(self, market_state: dict):
        self.volatility = market_state['volatility']
        self.performance_tracker = PerformanceTracker(market_state)

    def plot_metrics(self) -> None:
        """Plot performance metrics."""
        try:
            metrics = self.performance_tracker.get_metrics()
            
            # Для примера возьмём requests_per_second как метрику для отображения
            # В реальном приложении нужно собирать метрики за разные временные интервалы
            timestamps = list(range(5))  # Симуляция временных меток
            requests_per_second = [metrics['requests_per_second']] * 5  # Симуляция данных
            
            plt.figure(figsize=(10, 5))
            plt.plot(timestamps, requests_per_second, label='Requests per Second')
            plt.xlabel('Time')
            plt.ylabel('Requests per Second')
            plt.title('Performance Metrics Over Time')
            plt.legend()
            plt.grid()
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
