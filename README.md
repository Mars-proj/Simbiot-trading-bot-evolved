Simbiot Trading Bot Simbiot Trading Bot is an advanced, self-learning, and self-developing trading system designed for cryptocurrency markets. It deeply analyzes market conditions, scales to support thousands of users, and uses dynamic thresholds for trading decisions. Features: Self-Learning: Uses machine learning (LSTM) to predict prices and adapt to market changes. Self-Developing: Generates and optimizes trading strategies. Market Analysis: Performs deep market analysis with technical indicators (SMA, RSI, MACD, Bollinger Bands), volume analysis, anomaly detection, correlation analysis, and order book analysis. Scalability: Supports 1000+ users with asynchronous task processing (Celery), a REST API (Flask), user management (SQLite), and Telegram notifications. Dynamic Thresholds: Adjusts trading thresholds dynamically based on market conditions and ML predictions. Installation: 1. Clone the repository: git clone https://github.com/Mars-proj/Simbiot-trading-bot-full.git cd Simbiot-trading-bot-full 2. Create a virtual environment and install dependencies: python -m venv venv source venv/bin/activate pip install -r requirements.txt 3. Set up environment variables in a .env file: BINANCE_API_KEY=your_binance_api_key BINANCE_API_SECRET=your_binance_api_secret TELEGRAM_BOT_TOKEN=your_telegram_bot_token TELEGRAM_CHAT_ID=your_telegram_chat_id 4. Run the API server: python api_server.py 5. Run Celery worker: celery -A celery_app worker --loglevel=info 6. Run Celery beat for scheduled tasks: celery -A celery_app beat --loglevel=info Usage: 1. Log in to the API: curl -X POST http://localhost:5000/login -H "Content-Type: application/json" -d '{"user_id": "user1", "password": "password1"}' This will return a JWT token. 2. Start the bot: curl -X POST http://localhost:5000/start -H "Authorization: <your_token>" 3. Check the bot status: curl -X GET http://localhost:5000/status -H "Authorization: <your_token>" 4. Stop the bot: curl -X POST http://localhost:5000/stop -H "Authorization: <your_token>" Architecture: The system is modular, with components for trading, market analysis, machine learning, optimization, backtesting, and scalability. See trading_bot_graph.dot for a visual representation (can be visualized with Graphviz). Contributing: Contributions are welcome! Please submit a pull request or open an issue. License: MIT License
## Installation Status
- **Environment**: Ubuntu 22.04 LTS, Python 3.10.12
- **GPU**: NVIDIA Tesla T4, driver 535.230.02, CUDA 12.2, cuDNN 8.9.2.26
- **Libraries**: Installed successfully (see `requirements.txt`)
  - `vectorbt==0.27.2`
  - `tensorflow==2.17.0`
  - `torch==2.3.1` (CUDA-enabled)
  - Full list in `requirements.txt`
- **Database**: PostgreSQL 14 (database: `simbiot_trading`, user: `simbiot_user`)
- **Cache**: Redis
- **Status**: Ready for module development (e.g., `deal_pool`, `feature_engineering.py`)
## Installation Status
- **Environment**: Ubuntu 22.04 LTS, Python 3.10.12
- **GPU**: NVIDIA Tesla T4, driver 535.230.02, CUDA 12.2, cuDNN 8.9.2.26
- **Libraries**: Installed successfully (see `requirements.txt`)
  - `vectorbt==0.27.2`
  - `tensorflow==2.17.0` (GPU-enabled)
  - `torch==2.3.1` (CUDA-enabled)
  - Full list in `requirements.txt`
- **Database**: PostgreSQL 14 (database: `simbiot_trading`, user: `simbiot_user`)
- **Cache**: Redis (active)
- **Status**: Ready for module development (e.g., `deal_pool`, `feature_engineering.py`)
- **Notes**: TensorFlow warnings (`cuFFT`, `cuDNN`, `cuBLAS`) are non-critical and related to library registration.
