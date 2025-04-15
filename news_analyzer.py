from transformers import pipeline, AutoModelForSequenceClassification, AutoTokenizer
from utils.logging_setup import setup_logging
import requests
import torch

logger = setup_logging('news_analyzer')

class NewsAnalyzer:
    def __init__(self):
        # Инициализация BERT для анализа тональности
        self.sentiment_model_name = "nlptown/bert-base-multilingual-uncased-sentiment"
        self.sentiment_tokenizer = AutoTokenizer.from_pretrained(self.sentiment_model_name)
        self.sentiment_model = AutoModelForSequenceClassification.from_pretrained(self.sentiment_model_name)
        self.sentiment_model.eval()

        # Инициализация BERT для классификации тем
        self.topic_model_name = "distilbert-base-uncased"
        self.topic_tokenizer = AutoTokenizer.from_pretrained(self.topic_model_name)
        self.topic_model = AutoModelForSequenceClassification.from_pretrained(self.topic_model_name, num_labels=3)  # 3 категории: "регуляции", "макроэкономика", "технические сбои"
        self.topic_model.eval()
        self.topic_labels = ["regulations", "macroeconomics", "technical_issues"]

        self.api_key = "your_news_api_key"  # Замени на свой ключ NewsAPI
        self.base_url = "https://newsapi.org/v2/everything"

    def fetch_news(self, query="cryptocurrency regulation"):
        """Получаем новости через NewsAPI."""
        try:
            params = {
                "q": query,
                "apiKey": self.api_key,
                "language": "en",
                "sortBy": "publishedAt",
                "pageSize": 10
            }
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()
            articles = response.json().get("articles", [])
            logger.info(f"Fetched {len(articles)} articles for query: {query}")
            return articles
        except Exception as e:
            logger.error(f"Failed to fetch news: {str(e)}")
            return []

    def analyze_sentiment(self, text):
        """Анализируем тональность текста с помощью BERT."""
        try:
            inputs = self.sentiment_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
            with torch.no_grad():
                outputs = self.sentiment_model(**inputs)
                scores = torch.softmax(outputs.logits, dim=1).numpy()[0]
                sentiment = "POSITIVE" if scores.argmax() >= 3 else "NEGATIVE"  # nlptown модель возвращает 1-5 звёзд
                score = scores[scores.argmax()]
            return {"sentiment": sentiment, "score": float(score)}
        except Exception as e:
            logger.error(f"Failed to analyze sentiment: {str(e)}")
            return {"sentiment": "NEUTRAL", "score": 0.0}

    def classify_topic(self, text):
        """Классифицируем тему новости с помощью BERT."""
        try:
            inputs = self.topic_tokenizer(text, return_tensors="pt", truncation=True, padding=True, max_length=512)
            with torch.no_grad():
                outputs = self.topic_model(**inputs)
                scores = torch.softmax(outputs.logits, dim=1).numpy()[0]
                topic_idx = scores.argmax()
                topic = self.topic_labels[topic_idx]
                score = scores[topic_idx]
            return {"topic": topic, "score": float(score)}
        except Exception as e:
            logger.error(f"Failed to classify topic: {str(e)}")
            return {"topic": "unknown", "score": 0.0}

    def analyze_news(self, articles):
        """Анализируем новости на предмет регуляций или изменений."""
        try:
            critical_news = []
            for article in articles:
                title = article.get("title", "")
                description = article.get("description", "")
                text = f"{title} {description}" if description else title
                if not text:
                    continue

                # Анализ тональности
                sentiment_result = self.analyze_sentiment(text)
                sentiment = sentiment_result["sentiment"]
                sentiment_score = sentiment_result["score"]

                # Классификация темы
                topic_result = self.classify_topic(text)
                topic = topic_result["topic"]
                topic_score = topic_result["score"]

                # Проверяем, является ли новость критической
                if topic == "regulations" and topic_score > 0.7:
                    critical_news.append({
                        "title": title,
                        "sentiment": sentiment,
                        "sentiment_score": sentiment_score,
                        "topic": topic,
                        "topic_score": topic_score
                    })
            logger.info(f"Found {len(critical_news)} critical news items")
            return critical_news
        except Exception as e:
            logger.error(f"Failed to analyze news: {str(e)}")
            return []

    def should_pause_trading(self, critical_news):
        """Определяем, нужно ли приостановить торговлю."""
        try:
            for news in critical_news:
                if news['sentiment'] == "NEGATIVE" and news['sentiment_score'] > 0.7 and news['topic'] == "regulations":
                    logger.warning(f"Critical negative regulatory news detected: {news['title']}")
                    return True
            return False
        except Exception as e:
            logger.error(f"Failed to evaluate news impact: {str(e)}")
            return False
