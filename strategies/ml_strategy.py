import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
from utils.logging_setup import setup_logging
from .strategy import Strategy
from models.local_model_api import LocalModelAPI
from utils.news_fetcher import NewsFetcher
from utils.social_media_fetcher import SocialMediaFetcher
from textblob import TextBlob

logger = setup_logging('ml_strategy')

class MLStrategy(Strategy):
    def __init__(self, market_state: dict, market_data):
        super().__init__(market_state)
        self.model = LocalModelAPI(market_state, 'xgboost')
        self.lookback_period = 20
        self.market_data = market_data
        self.news_fetcher = NewsFetcher(market_state)
        self.social_media_fetcher = SocialMediaFetcher(market_state)

    async def get_sentiment_features(self, symbol: str) -> dict:
        """Fetch sentiment features from news and social media."""
        try:
            # Получаем новости и твиты асинхронно
            news_task = self.news_fetcher.fetch_news(symbol, page_size=5)
            tweets_task = self.social_media_fetcher.fetch_tweets(symbol, max_results=10)
            news, tweets = await asyncio.gather(news_task, tweets_task)

            # Анализируем настроения новостей
            news_sentiment = 0.0
            if news:
                for article in news:
                    description = article.get('description', '')
                    if description:
                        analysis = TextBlob(description)
                        news_sentiment += analysis.sentiment.polarity
                news_sentiment /= len(news)

            # Анализируем настроения твитов
            tweet_sentiment = 0.0
            if tweets:
                for tweet in tweets:
                    tweet_sentiment += tweet['polarity']
                tweet_sentiment /= len(tweets)

            return {
                'news_sentiment': news_sentiment,
                'tweet_sentiment': tweet_sentiment
            }
        except Exception as e:
            logger.error(f"Failed to fetch sentiment features for {symbol}: {str(e)}")
            return {'news_sentiment': 0.0, 'tweet_sentiment': 0.0}

    async def generate_signal(self, symbol: str, timeframe: str = '1h', limit: int = 30, exchange_name: str = 'mexc') -> str:
        """Generate a trading signal using a machine learning model with sentiment features."""
        try:
            # Получаем данные с биржи
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if len(klines) < self.lookback_period:
                logger.warning(f"Not enough data for {symbol} to generate ML prediction")
                return "hold"

            # Получаем ценовые данные
            closes = [kline['close'] for kline in klines[-self.lookback_period:]]

            # Получаем настроения из новостей и соцсетей
            sentiment_features = await self.get_sentiment_features(symbol)

            # Формируем признаки для модели
            features = closes + [sentiment_features['news_sentiment'], sentiment_features['tweet_sentiment']]
            prediction = self.model.predict([features])[0]

            price = klines[-1]['close']
            if prediction > price:
                signal = "buy"
            elif prediction < price:
                signal = "sell"
            else:
                signal = "hold"

            logger.info(f"Generated signal for {symbol}: {signal} (Prediction: {prediction}, Price: {price})")
            return signal
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {str(e)}")
            raise

if __name__ == "__main__":
    # Test run
    import asyncio
    from data_sources.market_data import MarketData
    from symbol_filter import SymbolFilter
    market_state = {'volatility': 0.3}
    market_data = MarketData(market_state)
    strategy = MLStrategy(market_state, market_data=market_data)
    symbol_filter = SymbolFilter(market_state, market_data=market_data)
    
    async def main():
        symbols = await strategy.market_data.get_symbols('mexc')
        symbols = await symbol_filter.filter_symbols(symbols, 'mexc')
        
        if symbols:
            signal = await strategy.generate_signal(symbols[0], '1h', 30, 'mexc')
            print(f"Signal for {symbols[0]}: {signal}")
        else:
            print("No symbols available for testing")

    asyncio.run(main())
