import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import asyncio
import numpy as np
from utils.logging_setup import setup_logging
from utils.news_fetcher import NewsFetcher
from utils.social_media_fetcher import SocialMediaFetcher
from models.local_model_api import LocalModelAPI
from .strategy import Strategy

logger = setup_logging('ml_strategy')

class MLStrategy(Strategy):
    def __init__(self, market_state: dict, market_data):
        super().__init__(market_state, market_data=market_data)
        self.volatility = market_state['volatility']
        self.model = LocalModelAPI()
        self.news_fetcher = NewsFetcher()
        self.social_media_fetcher = SocialMediaFetcher()
        self.is_trained = False  # Флаг для отслеживания состояния модели

    def prepare_features(self, klines: list, tweets: list, news_articles: list) -> list:
        """Prepare features for ML model from klines, tweets, and news."""
        try:
            # Извлечение цен закрытия и объёмов
            close_prices = [kline['close'] for kline in klines]
            volumes = [kline['volume'] for kline in klines]
            
            # Вычисление технических индикаторов
            price_change = (close_prices[-1] - close_prices[0]) / close_prices[0] if close_prices[0] != 0 else 0
            avg_volume = sum(volumes) / len(volumes) if volumes else 0
            
            # Анализ настроений из твитов и новостей
            tweet_sentiment = sum(self.news_fetcher.analyze_sentiment(tweet) for tweet in tweets) / len(tweets) if tweets else 0
            news_sentiment = sum(self.news_fetcher.analyze_sentiment(article['title']) for article in news_articles) / len(news_articles) if news_articles else 0
            
            # Формирование признаков
            features = [
                price_change,
                avg_volume,
                self.volatility,
                tweet_sentiment,
                news_sentiment
            ]
            return features
        except Exception as e:
            logger.error(f"Failed to prepare features: {str(e)}")
            raise

    async def train_model(self, symbol: str, timeframe: str, limit: int, exchange_name: str):
        """Train the ML model with historical data."""
        try:
            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines or len(klines) < 2:
                logger.warning(f"Not enough data for {symbol} to train ML model")
                return

            # Fetch news and social media data
            tweets = self.social_media_fetcher.fetch_tweets(symbol)
            news_articles = self.news_fetcher.fetch_news(symbol)

            # Prepare features and labels
            features_list = []
            labels_list = []
            for i in range(len(klines) - 1):
                subset_klines = klines[max(0, i-10):i+1]  # Используем последние 10 свечей
                features = self.prepare_features(subset_klines, tweets, news_articles)
                features_list.append(features)
                # Метка: 1 (рост), если следующая цена выше текущей, иначе 0
                labels_list.append(1 if klines[i+1]['close'] > klines[i]['close'] else 0)

            # Train the model
            self.model.train(features_list, labels_list)
            self.is_trained = True
            logger.info(f"ML model trained for {symbol}")
        except Exception as e:
            logger.error(f"Failed to train ML model for {symbol}: {str(e)}")
            raise

    async def generate_signal(self, symbol: str, timeframe: str = '1m', limit: int = 1, exchange_name: str = 'mexc') -> str:
        """Generate a trading signal using ML model predictions."""
        try:
            # Train the model if not already trained
            if not self.is_trained:
                await self.train_model(symbol, timeframe, max(limit, 100), exchange_name)

            klines = await self.market_data.get_klines(symbol, timeframe, limit, exchange_name)
            if not klines:
                logger.warning(f"No data for {symbol} to generate ML signal")
                return "hold"

            # Fetch news and social media data
            tweets = self.social_media_fetcher.fetch_tweets(symbol)
            news_articles = self.news_fetcher.fetch_news(symbol)

            # Prepare features
            features = self.prepare_features(klines, tweets, news_articles)

            # Use the model to predict
            prediction = self.model.predict([features])[0]
            logger.info(f"Generated ML signal for {symbol}: {prediction}")
            return "buy" if prediction > 0.5 else "sell"
        except Exception as e:
            logger.error(f"Error generating signal for {symbol}: {str(e)}")
            raise
