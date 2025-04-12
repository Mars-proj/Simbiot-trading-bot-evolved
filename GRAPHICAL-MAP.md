# Graphical Map for Simbiot-trading-bot-full

Below is a detailed graphical representation of the project architecture.

## Detailed Architecture Diagram
+-------------------+
|   TradingBotCore  |
|  (core.py)        |
+-------------------+
|
| Interacts with
v
+-------------------+    +-------------------+    +-------------------+    +-------------------+
| StrategyManager   |    | TradeExecutor     |    | BacktestManager   |    | Monitoring        |
| (strategies/)     |    | (trading/)        |    | (learning/)       |    | (monitoring/)     |
+-------------------+    +-------------------+    +-------------------+    +-------------------+
|                       |                       |                       |
| Uses                  | Executes trades      | Runs backtests        | Monitors system
v                       v                       v                       v
+-------------------+    +-------------------+    +-------------------+    +-------------------+
| Strategies        |    | Order/Position    |    | BacktestCycle     |    | AlertManager      |
| (bollinger, rsi)  |    | Managers          |    | GeneticOptimizer  |    | PerformanceMetrics|
| (ml_strategy)     |    +-------------------+    +-------------------+    +-------------------+
+-------------------+              |                       |                       |
|                         | Uses data             | Uses data             | Uses data
| Uses data               v                       v                       v
|              +-------------------+    +-------------------+    +-------------------+
|              | MarketData        |    | MarketData        |    | MarketData        |
|              | (data_sources/)   |    | (data_sources/)   |    | (data_sources/)   |
|              +-------------------+    +-------------------+    +-------------------+
|                       |                       |                       |
| Provides data         | Provides data         | Provides data         | Provides data
v                       v                       v                       v
+-------------------+    +-------------------+    +-------------------+    +-------------------+
| SocialMedia       |    | Binance/Kraken    |    | Binance/Kraken    |    | Binance/Kraken    |
| Fetcher (utils/)  |    | APIs              |    | APIs              |    | APIs              |
+-------------------+    +-------------------+    +-------------------+    +-------------------+

+-------------------+    +-------------------+    +-------------------+    +-------------------+
| UIManager         |    | Models            |    | Utils             |    | Analysis          |
| (ui/)             |    | (models/)         |    | (utils/)          |    | (analysis/)       |
+-------------------+    +-------------------+    +-------------------+    +-------------------+
|                       |                       |                       |
| Displays data         | Provides ML           | Provides utilities    | Provides analytics
v                       v                       v                       v
+-------------------+    +-------------------+    +-------------------+    +-------------------+
| Dashboard/Charts  |    | XGBoost/LSTM      |    | Cache/Telegram    |    | Liquidity/        |
| TradeVisualizer   |    | LocalModelAPI     |    | RateLimiter       |    | Volatility        |
+-------------------+    +-------------------+    +-------------------+    +-------------------+

+-------------------+
| Docs              |
| (docs/)           |
+-------------------+
|
| Provides documentation
v
+-------------------+
| README/ROADMAP    |
| IMPROVEMENTS      |
+-------------------

## Description
- **TradingBotCore**: Central module that orchestrates trading, backtesting, and monitoring.
- **StrategyManager**: Manages trading strategies and generates signals. ML strategies use `SocialMediaFetcher` for sentiment analysis.
- **TradeExecutor**: Executes trades using order and position management.
- **BacktestManager**: Manages backtesting cycles and optimization.
- **Monitoring**: Monitors system performance and sends alerts.
- **UIManager**: Manages UI components for visualization.
- **Models**: Provides machine learning models for predictions.
- **Utils**: Provides utility functions (caching, notifications, social media fetching, etc.).
- **Analysis**: Provides analytics for liquidity and volatility.
- **MarketData**: Fetches real-time data from exchanges (Binance, Kraken).
- **Docs**: Contains project documentation (README, ROADMAP, IMPROVEMENTS).
