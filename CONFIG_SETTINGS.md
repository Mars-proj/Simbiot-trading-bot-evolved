# Configuration Settings from Unused Modules

## Strategy Settings
- **Arbitrage Strategy:**
  - `min_price_diff = 0.01` (Minimum price difference for arbitrage)
- **Mean Reversion Strategy:**
  - `period = 20` (Period for calculating mean)
  - `deviation_threshold = 2 * volatility` (Threshold for deviation)
- **Grid Strategy:**
  - `grid_size = 0.005` (Grid size)
  - `levels = 10` (Number of grid levels)
- **Breakout Strategy:**
  - `breakout_period = 50` (Period for breakout)
  - `confirmation_threshold = 1.5 * atr` (Confirmation threshold)
- **Scalping Strategy:**
  - `timeframe = "1m"` (Timeframe for scalping)
  - `min_profit = 0.002` (Minimum profit target)
- **Volatility Strategy:**
  - `volatility_threshold = 0.5` (Volatility threshold)
- **Trend Strategy:**
  - `trend_period = 100` (Period for trend detection)
  - `adx_threshold = 20 + volatility * 10` (ADX threshold)

## Machine Learning Settings
- **XGBoost Model:**
  - `max_depth = 6` (Maximum depth of trees)
  - `n_estimators = 100` (Number of estimators)
- **RNN Model:**
  - `units = 64` (Number of units in layer)
  - `dropout_rate = 0.2` (Dropout rate)
- **LSTM Model:**
  - `units = 128` (Number of units in layer)
  - `lookback = 20` (Lookback period)
- **Base Model:**
  - `epochs = 10` (Training epochs)
  - `batch_size = 32` (Batch size)
- **ML Trainer:**
  - `retrain_interval = 300` (Retraining interval in seconds)
- **Retraining Manager:**
  - `error_threshold = 0.1` (Error threshold for retraining)
- **Threshold Predictor:**
  - `prediction_period = 14` (Period for threshold prediction)

## Exchange Support Settings
- **Kraken API:**
  - `rate_limit = 20` (Requests per minute)
- **RoboForex API:**
  - `supported_timeframes = ["1m", "5m", "1h"]` (Supported timeframes)
- **Exchange Factory:**
  - `supported_exchanges = ["mexc", "binance", "kucoin"]` (Supported exchanges)

## Risk Management Settings
- **Risk Manager:**
  - `max_risk_per_trade = 0.02` (Maximum risk per trade)
- **Risk Calculator:**
  - `risk_factor = 1.5 * volatility` (Risk factor)
- **Position Manager:**
  - `max_position_size = 0.1` (Maximum position size)
- **Order Manager:**
  - `order_timeout = 60` (Order timeout in seconds)
- **Trade Executor:**
  - `min_order_volume = 0.001` (Minimum order volume)

## Logging and Monitoring Settings
- **Alert Manager:**
  - `alert_interval = 300` (Alert interval in seconds)
- **Performance Metrics:**
  - `metrics = ["profit", "sharpe_ratio"]` (Metrics to track)
- **Performance Monitor:**
  - `monitor_frequency = 60` (Monitoring frequency in seconds)
- **Trade Logger:**
  - `log_format = "%(asctime)s - %(levelname)s - %(message)s"` (Log format)
- **Health Checker:**
  - `check_interval = 120` (Health check interval in seconds)
- **Monitoring:**
  - `cpu_usage_threshold = 80` (CPU usage threshold)
  - `memory_usage_threshold = 75` (Memory usage threshold)

## Scalability Settings
- **API Rate Limiter:**
  - `requests_per_minute = 60` (Requests per minute limit)
- **Cache Manager:**
  - `cache_ttl = 600` (Cache time-to-live in seconds)
- **Celery App:**
  - `broker = "redis://localhost:6379/0"` (Broker URL)
  - `task_serializer = "json"` (Task serializer)
- **WebSocket Manager:**
  - `timeout = 30` (WebSocket timeout in seconds)
