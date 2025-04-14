# Simbiot Trading Bot System Information

## Overview
This document provides key information about the Simbiot Trading Bot system, including the number of modules, their structure, and purpose.

## System Details
- **Date:** April 14, 2025
- **Operating System:** Linux Debian 6.1.0-29-amd64
- **Repository:** https://github.com/Mars-proj/Simbiot-trading-bot-new.git
- **Total Number of Modules:** 97

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
  - `models/lstm_model.py`: LSTM model.
  - `models/rnn_model.py`: RNN model.
  - `__init__.py`

- **Strategies (15):**
  - `strategies/strategy.py`: Base class for strategies.
  - `strategies/bollinger_strategy.py`: Bollinger Bands strategy.
  - `strategies/rsi_strategy.py`: RSI strategy.
  - `strategies/macd_strategy.py`: MACD strategy.
  - `strategies/ml_strategy.py`: ML-based strategy.
  - `strategies/arbitrage_strategy.py`: Arbitrage strategy (dynamic).
  - `strategies/mean_reversion_strategy.py`: Mean reversion strategy (dynamic).
  - `strategies/grid_strategy.py`: Grid trading strategy (dynamic).
  - `strategies/breakout_strategy.py`: Breakout strategy.
  - `strategies/scalping_strategy.py`: Scalping strategy.
  - `strategies/trend_strategy.py`: Trend-following strategy.
  - `strategies/volatility_strategy.py`: Volatility-based strategy.
  - `strategies/signal_generator.py`: Signal generation utilities.
  - `strategies/strategy_manager.py`: Manages strategy execution.
  - `strategies/strategy_optimizer.py`: Optimizes strategy parameters.
  - `__init__.py`

- **Risk Management (5):**
  - `risk_management/risk_manager.py`: Dynamic risk calculation.
  - `risk_management/position_manager.py`: Position size management.
  - `risk_management/risk_calculator.py`: Risk calculation utilities.
  - `risk_management/trade_executor.py`: Trade execution with risk controls.
  - `risk_management/trade_logger.py`: Logging trades for risk analysis.
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

- **Unused Modules (24):**
  - Located in `unused_modules/`. These modules are preserved for potential future use. Examples include `alert_manager.py`, `health_checker.py`, etc. Useful settings from these modules are documented in `CONFIG_SETTINGS.md`.

## Goals and Compliance
- **Automated Trading:** Fully supported by core modules and strategies.
- **Dynamic Strategies:** Enhanced with new strategies (arbitrage, mean_reversion, grid) using dynamic thresholds.
- **Machine Learning:** Enhanced with `online_learning.py` and models (XGBoost, Transformer, LSTM, RNN).
- **Multiple Exchanges:** Supported by multiple API modules in `data_sources/`.
- **Risk Management:** Enhanced with `risk_management/` modules (stop-loss, position monitoring).
- **Logging and Monitoring:** Supported by `logging_setup.py`.
- **Scalability:** System is ready for improvements (Redis, Celery, etc.).
