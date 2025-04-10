# Future Improvements and Saved Settings

This file contains useful settings and ideas from modules that were either not working or removed but may be needed in the future.

## ML and Self-Learning
- **ml_data_preparer.py**: Concept of data preparation for ML (removing NaNs with `dropna()`). Future: Add normalization, feature extraction, outlier handling.
- **ml_model_trainer.py**: Concept of training a model by `model_id`, using `LinearRegression` from `sklearn`. Future: Add data loading, training, and model saving.
- **ml_predictor.py**: Interface `predict(data: dict) -> float`. Future: Add model loading and real predictions.
- **online_learning.py**: Interface `update_model(data: dict)`. Future: Add real online learning logic.

## Self-Development and Dynamic Thresholds
- **genetic_optimizer.py**: Parameters `population_size=50`, `generations=10`. Structure of genetic algorithm (initialize, evolve, select best). Future: Add selection, crossover, mutation logic.
- **strategy_generator.py**: Interface `generate_strategy() -> Strategy`, parameter `threshold=10000`. Future: Add dynamic strategy generation.
- **strategy_param_generator.py**: Interface `generate_params() -> Dict`, parameter `threshold=10000`. Future: Add dynamic parameter generation.

## Market Analysis
- **symbol_filter.py**: Interface `filter_symbols(symbols: List[str], min_volume: float) -> List[str]`, parameter `min_volume`. Future: Add real volume-based filtering.

## Scalability
- **telegram_notifier.py**: Interface `send_telegram_message(message: str)`. Future: Add real Telegram notification logic.
- **queue_manager.py**: Function `add_to_queue(task: str, *args)`. Moved to `celery_app.py`.

## Other
- **global_objects.py**: Parameters `default_timeframe="1h"`, `default_symbol="BTC/USDT"`. Moved to `utils.py` or `config.py`.
- **monitoring.py**: Idea of monitoring bot performance. Future: Add real monitoring (metrics, alerts).
