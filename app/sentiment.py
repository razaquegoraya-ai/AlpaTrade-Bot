import feedparser
import httpx
from vaderSentiment.vaderSentiment import SentimentIntensityAnalyzer
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import logging
import re
import asyncio

from app.models import NewsItem

logger = logging.getLogger(__name__)


class NewsSentimentAnalyzer:
    """News sentiment analysis for trading decisions"""
    
    def __init__(self):
        self.analyzer = SentimentIntensityAnalyzer()
        self.news_sources = [
            "https://feeds.finance.yahoo.com/rss/2.0/headline",
            "https://feeds.marketwatch.com/marketwatch/topstories/",
            "https://feeds.bloomberg.com/markets/news.rss",
            "https://www.cnbc.com/id/100003114/device/rss/rss.html",
            "https://feeds.reuters.com/news/wealth",
            "https://feeds.finance.yahoo.com/rss/2.0/headline?s=^GSPC&region=US&lang=en-US"
        ]
        
    async def fetch_news(self, symbols: List[str] = None, hours_back: int = 24) -> List[Dict[str, Any]]:
        """
        Fetch news from RSS feeds
        
        Args:
            symbols: List of symbols to filter news for
            hours_back: How many hours back to fetch news
            
        Returns:
            List of news items
        """
        news_items = []
        cutoff_time = datetime.utcnow() - timedelta(hours=hours_back)
        
        async with httpx.AsyncClient(timeout=30.0) as client:
            for source_url in self.news_sources:
                try:
                    response = await client.get(source_url)
                    if response.status_code == 200:
                        feed = feedparser.parse(response.content)
                        
                        for entry in feed.entries:
                            try:
                                # Parse publication date
                                pub_date = None
                                if hasattr(entry, 'published_parsed') and entry.published_parsed:
                                    pub_date = datetime(*entry.published_parsed[:6])
                                elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                                    pub_date = datetime(*entry.updated_parsed[:6])
                                
                                if pub_date and pub_date < cutoff_time:
                                    continue
                                
                                # Extract content
                                title = entry.get('title', '')
                                summary = entry.get('summary', '')
                                link = entry.get('link', '')
                                
                                # Check if news is relevant to our symbols
                                if symbols:
                                    relevant_symbols = self._extract_symbols_from_text(
                                        f"{title} {summary}", symbols
                                    )
                                    if not relevant_symbols:
                                        continue
                                else:
                                    relevant_symbols = []
                                
                                news_item = {
                                    'title': title,
                                    'content': summary,
                                    'url': link,
                                    'published_at': pub_date or datetime.utcnow(),
                                    'source': source_url,
                                    'symbols': relevant_symbols
                                }
                                
                                news_items.append(news_item)
                                
                            except Exception as e:
                                logger.error(f"Error parsing news entry: {e}")
                                continue
                                
                except Exception as e:
                    logger.error(f"Error fetching news from {source_url}: {e}")
                    continue
        
        return news_items
    
    def _extract_symbols_from_text(self, text: str, symbols: List[str]) -> List[str]:
        """
        Extract relevant symbols from news text
        
        Args:
            text: News text to analyze
            symbols: List of symbols to look for
            
        Returns:
            List of symbols found in the text
        """
        found_symbols = []
        text_lower = text.lower()
        
        for symbol in symbols:
            symbol_lower = symbol.lower()
            
            # Check for exact symbol match
            if symbol_lower in text_lower:
                found_symbols.append(symbol)
                continue
            
            # Check for company name variations (basic implementation)
            # This could be enhanced with a company name to symbol mapping
            symbol_patterns = {
                'AAPL': ['apple', 'iphone', 'ipad', 'macbook'],
                'MSFT': ['microsoft', 'azure', 'office', 'windows'],
                'GOOGL': ['google', 'alphabet', 'youtube', 'android'],
                'AMZN': ['amazon', 'aws', 'prime'],
                'TSLA': ['tesla', 'elon musk', 'electric vehicle'],
                'META': ['facebook', 'meta', 'instagram', 'whatsapp'],
                'NVDA': ['nvidia', 'gpu', 'ai chip'],
                'SPY': ['spy', 'spdr', 's&p 500', 'sp500'],
                'QQQ': ['qqq', 'nasdaq', 'invesco'],
                'IWM': ['iwm', 'russell 2000', 'small cap']
            }
            
            if symbol in symbol_patterns:
                for pattern in symbol_patterns[symbol]:
                    if pattern in text_lower:
                        found_symbols.append(symbol)
                        break
        
        return found_symbols
    
    def analyze_sentiment(self, text: str) -> Dict[str, Any]:
        """
        Analyze sentiment of text using VADER
        
        Args:
            text: Text to analyze
            
        Returns:
            Sentiment analysis results
        """
        try:
            scores = self.analyzer.polarity_scores(text)
            
            # Determine sentiment label
            if scores['compound'] >= 0.05:
                label = 'positive'
            elif scores['compound'] <= -0.05:
                label = 'negative'
            else:
                label = 'neutral'
            
            return {
                'compound': scores['compound'],
                'positive': scores['pos'],
                'negative': scores['neg'],
                'neutral': scores['neu'],
                'label': label
            }
            
        except Exception as e:
            logger.error(f"Error analyzing sentiment: {e}")
            return {
                'compound': 0.0,
                'positive': 0.0,
                'negative': 0.0,
                'neutral': 1.0,
                'label': 'neutral'
            }
    
    async def get_sentiment_for_symbols(
        self,
        symbols: List[str],
        hours_back: int = 24
    ) -> Dict[str, Dict[str, Any]]:
        """
        Get sentiment analysis for specific symbols
        
        Args:
            symbols: List of symbols to analyze
            hours_back: How many hours back to fetch news
            
        Returns:
            Dictionary mapping symbols to sentiment data
        """
        try:
            # Fetch news
            news_items = await self.fetch_news(symbols, hours_back)
            
            # Group news by symbol
            symbol_news = {symbol: [] for symbol in symbols}
            
            for item in news_items:
                for symbol in item.get('symbols', []):
                    if symbol in symbol_news:
                        symbol_news[symbol].append(item)
            
            # Analyze sentiment for each symbol
            symbol_sentiment = {}
            
            for symbol, news_list in symbol_news.items():
                if not news_list:
                    symbol_sentiment[symbol] = {
                        'sentiment_score': 0.0,
                        'sentiment_label': 'neutral',
                        'news_count': 0,
                        'confidence': 0.0
                    }
                    continue
                
                # Combine all news text for this symbol
                combined_text = ' '.join([
                    f"{item['title']} {item.get('content', '')}"
                    for item in news_list
                ])
                
                # Analyze sentiment
                sentiment = self.analyze_sentiment(combined_text)
                
                # Calculate confidence based on news count and sentiment strength
                confidence = min(len(news_list) / 5.0, 1.0) * abs(sentiment['compound'])
                
                symbol_sentiment[symbol] = {
                    'sentiment_score': sentiment['compound'],
                    'sentiment_label': sentiment['label'],
                    'news_count': len(news_list),
                    'confidence': confidence,
                    'recent_news': news_list[:3]  # Keep top 3 recent news items
                }
            
            return symbol_sentiment
            
        except Exception as e:
            logger.error(f"Error getting sentiment for symbols: {e}")
            return {symbol: {
                'sentiment_score': 0.0,
                'sentiment_label': 'neutral',
                'news_count': 0,
                'confidence': 0.0
            } for symbol in symbols}
    
    def filter_signals_by_sentiment(
        self,
        signals: List[Any],
        sentiment_data: Dict[str, Dict[str, Any]],
        min_sentiment_score: float = -0.1
    ) -> List[Any]:
        """
        Filter trading signals based on sentiment analysis
        
        Args:
            signals: List of trading signals
            sentiment_data: Sentiment data for symbols
            min_sentiment_score: Minimum sentiment score threshold
            
        Returns:
            Filtered list of signals
        """
        filtered_signals = []
        
        for signal in signals:
            symbol = signal.symbol
            sentiment_info = sentiment_data.get(symbol, {})
            sentiment_score = sentiment_info.get('sentiment_score', 0.0)
            
            # For buy signals, require positive or neutral sentiment
            if signal.side.value == 'buy':
                if sentiment_score >= min_sentiment_score:
                    filtered_signals.append(signal)
            # For sell signals, sentiment is less critical
            else:
                filtered_signals.append(signal)
        
        return filtered_signals
    
    async def get_market_sentiment(self, hours_back: int = 24) -> Dict[str, Any]:
        """
        Get overall market sentiment
        
        Args:
            hours_back: How many hours back to analyze
            
        Returns:
            Market sentiment data
        """
        try:
            # Fetch general market news
            news_items = await self.fetch_news(hours_back=hours_back)
            
            if not news_items:
                return {
                    'sentiment_score': 0.0,
                    'sentiment_label': 'neutral',
                    'news_count': 0,
                    'confidence': 0.0
                }
            
            # Combine all news text
            combined_text = ' '.join([
                f"{item['title']} {item.get('content', '')}"
                for item in news_items
            ])
            
            # Analyze sentiment
            sentiment = self.analyze_sentiment(combined_text)
            
            # Calculate confidence
            confidence = min(len(news_items) / 10.0, 1.0) * abs(sentiment['compound'])
            
            return {
                'sentiment_score': sentiment['compound'],
                'sentiment_label': sentiment['label'],
                'news_count': len(news_items),
                'confidence': confidence
            }
            
        except Exception as e:
            logger.error(f"Error getting market sentiment: {e}")
            return {
                'sentiment_score': 0.0,
                'sentiment_label': 'neutral',
                'news_count': 0,
                'confidence': 0.0
            }
