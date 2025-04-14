# Simbiot Trading Bot System Information

## Overview
This document provides key information about the Simbiot Trading Bot system, including the number of modules, their structure, and purpose.

## System Details
- **Date:** April 14, 2025
- **Operating System:** Linux Debian 6.1.0-29-amd64
- **Repository:** https://github.com/Mars-proj/Simbiot-trading-bot-new.git
- **Total Number of Modules:** 102

## Module Structure
- **Core Modules (4):**
  - `start_trading_all.py`: Entry point for the trading system.
  - `core.py`: Core trading logic, including risk management.
  - `symbol_filter.py`: Filters trading symbols based on liquidity and volatility.
  - `volatility_analyzer.py`: Analyzes market volatility using GARCH.

- **Data Sources (12):**
  - `data_sources/market_data.py`: Abstract class for market data.
  - `data_sources/mexc_api.py`: API for MEXC exchange.
  - `data_sources/binance_api.py`: API for Binance exchange.
  - `data_sources/kucoin_api.py`: API for KuCoin exchange.
  - `data_sources/huobi_api.py`: API for Huobi exchange.
  - `data_sources/bybit_api.py`: API for Bybit exchange.
  - `data_sources/bitstamp_api.py`: API for Bitstamp exchange.
  - `data_sources/coinbase_api.py`: API for Coinbase exchange.
  - `data_sources/exchange_detector.py`: Detects exchange type.
  - `data_sources/price_fetcher.py`: Fetches price data.
  - `data_sources/volume_analyzer.py`: Analyzes trading volume.
  - `data_sources/websocket_manager.py`: Manages WebSocket connections.
  - `__init__.py`

- **Learning (9):**
  - `learning/online_learning.py`: Online learning for ML models.
  - `learning/strategy_optimizer.py`: Strategy optimization.
  - `learning/backtest_manager.py`: Backtesting management.
  - `learning/backtester.py`: Backtesting framework.
  - `learning/genetic_optimizer.py`: Genetic optimization for strategies.
  - `learning/trade_evaluator.py`: Evaluates trade performance.
  - `learning/ml_trainer.py`: ML model training.
  - `learning/retraining_manager.py`: Manages model retraining.
  - `__init__.py`

- **Models (5):**
  - `models/local_model_api.py`: XGBoost model.
  - `models/transformer_model.py`: Transformer model (Keras/TensorFlow).
  - `models/base_model.py`: Base class for models.
  - `models/lstm_model.py`: LSTM model.
  - `models/rnn_model.py`: RNN model.
  - `__init__.py`

- **Strategies (12):**
  - `strategies/strategy.py`: Base class for strategies.
  - `strategies/bollinger_strategy.py`: Bollinger Bands strategy.
  - `strategies/rsi_strategy.py`: RSI strategy.
  - `strategies/macd_strategy.py`: MACD strategy.
  - `strategies/ml_strategy.py`: ML-based strategy.
  - `strategies/arbitrage_strategy.py`: Arbitrage strategy.
  - `strategies/mean_reversion_strategy.py`: Mean reversion strategy.
  - `strategies/grid_strategy.py`: Grid trading strategy.
  - `strategies/breakout_strategy.py`: Breakout strategy.
  - `strategies/scalping_strategy.py`: Scalping strategy.
  - `strategies/trend_strategy.py`: Trend-following strategy.
  - `strategies/volatility_strategy.py`: Volatility-based strategy.
  - `__init__.py`

- **Utils (11):**
  - `utils/logging_setup.py`: Logging setup.
  - `utils/data_utils.py`: Data processing utilities.
  - `utils/api_rate_limiter.py`: API rate limiting.
  - `utils/api_utils.py`: API utilities.
  - `utils/cache_manager.py`: Cache management.
  - `utils/config_loader.py`: Configuration loader.
  - `utils/error_handler.py`: Error handling.
  - `utils/get_chat_id.py`: Retrieves Telegram chat ID.
  - `utils/market_data_collector.py`: Collects market data.
  - `utils/performance_tracker.py`: Tracks performance.
  - `utils/time_utils.py`: Time utilities.
  - `__init__.py`

- **Unused Modules (29):**
  - Located in `unused_modules/`. These modules are preserved for potential future use. Examples include `arbitrage_strategy.py`, `celery_app.py`, `risk_manager.py`, etc. Useful settings from these modules are documented in `CONFIG_SETTINGS.md`.

## Goals and Compliance
- **Automated Trading:** Fully supported by core modules and strategies.
- **Dynamic Strategies:** Strategies adapt thresholds based on volatility.
- **Machine Learning:** Supported by `online_learning.py` and models.
- **Multiple Exchanges:** Supported by multiple API modules in `data_sources/`.
- **Risk Management:** Implemented in `core.py` (stop-loss, position monitoring).
- **Logging and Monitoring:** Supported by `logging_setup.py`.
- **Scalability:** System is ready for improvements (Redis, Celery, etc.).
