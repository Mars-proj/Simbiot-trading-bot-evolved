# Simbiot Trading Bot System Information

## Overview
This document provides key information about the Simbiot Trading Bot system, including the number of modules, their structure, and purpose.

## System Details
- **Date:** April 14, 2025
- **Operating System:** Linux Debian 6.1.0-29-amd64
- **Repository:** https://github.com/Mars-proj/Simbiot-trading-bot-full.git
- **Total Number of Modules:** 104

## Module Structure
- **Core Modules (4):**
  - `start_trading_all.py`: Entry point for the trading system.
  - `core.py`: Core trading logic, including risk management.
  - `symbol_filter.py`: Filters trading symbols based on liquidity and volatility.
  - `volatility_analyzer.py`: Analyzes market volatility using GARCH.

- **Data Sources (6):**
  - `data_sources/market_data.py`: Abstract class for market data.
  - `data_sources/mexc_api.py`: API for MEXC exchange.
  - `data_sources/binance_api.py`: API for Binance exchange.
  - `data_sources/kucoin_api.py`: API for KuCoin exchange.
  - `data_sources/huobi_api.py`: API for Huobi exchange.
  - `data_sources/bybit_api.py`: API for Bybit exchange.

- **Learning (3):**
  - `learning/online_learning.py`: Online learning for ML models.
  - `learning/strategy_optimizer.py`: Strategy optimization.
  - `learning/backtest_manager.py`: Backtesting management.

- **Models (2):**
  - `models/local_model_api.py`: XGBoost model.
  - `models/transformer_model.py`: Transformer model (Keras/TensorFlow).

- **Strategies (6):**
  - `strategies/strategy.py`: Base class for strategies.
  - `strategies/bollinger_strategy.py`: Bollinger Bands strategy.
  - `strategies/rsi_strategy.py`: RSI strategy.
  - `strategies/macd_strategy.py`: MACD strategy.
  - `strategies/ml_strategy.py`: ML-based strategy.
  - `__init__.py`

- **Utils (3):**
  - `utils/logging_setup.py`: Logging setup.
  - `utils/data_utils.py`: Data processing utilities.
  - `__init__.py`

- **Unused Modules (84):**
  - Located in `unused_modules/`. These modules are not currently used but preserved for future reference. Examples include `social_media_fetcher.py`, `news_fetcher.py`, `celery_app.py`, etc.

## Goals and Compliance
- **Automated Trading:** Fully supported by core modules and strategies.
- **Dynamic Strategies:** Strategies adapt thresholds based on volatility.
- **Machine Learning:** Supported by `online_learning.py` and models.
- **Multiple Exchanges:** Supported by multiple API modules in `data_sources/`.
- **Risk Management:** Implemented in `core.py` (stop-loss, position monitoring).
- **Logging and Monitoring:** Supported by `logging_setup.py`.
- **Scalability:** System is ready for improvements (Redis, Celery, etc.).
