"""
Sentiment Analysis Module using TextBlob.

Analyzes user messages for emotional tone and returns:
- Sentiment polarity (-1 to 1)
- Sentiment category (positive/neutral/negative)
- Corresponding emoji
"""

try:
    from textblob import TextBlob
    TEXTBLOB_AVAILABLE = True
except ImportError:
    TEXTBLOB_AVAILABLE = False
    print("[WARNING] TextBlob not installed. Sentiment analysis will use basic rules.")

import config.settings as cfg


class SentimentAnalyzer:
    """Analyze sentiment of text messages."""
    
    def __init__(self):
        self.emoji_map = cfg.SENTIMENT_EMOJIS
    
    def analyze(self, text: str) -> dict:
        """
        Analyze sentiment of given text.
        
        Args:
            text: Input text to analyze
        
        Returns:
            Dictionary with polarity, category, and emoji
        """
        if not text:
            return {
                'polarity': 0.0,
                'category': 'neutral',
                'emoji': self.emoji_map['neutral']
            }
        
        if TEXTBLOB_AVAILABLE:
            return self._analyze_with_textblob(text)
        else:
            return self._analyze_basic(text)
    
    def _analyze_with_textblob(self, text: str) -> dict:
        """Use TextBlob for accurate sentiment analysis."""
        try:
            blob = TextBlob(text)
            polarity = blob.sentiment.polarity
            
            # Categorize based on polarity
            if polarity > 0.1:
                category = 'positive'
            elif polarity < -0.1:
                category = 'negative'
            else:
                category = 'neutral'
            
            return {
                'polarity': round(polarity, 2),
                'category': category,
                'emoji': self.emoji_map[category]
            }
        except Exception as e:
            print(f"[ERROR] TextBlob analysis failed: {e}")
            return self._analyze_basic(text)
    
    def _analyze_basic(self, text: str) -> dict:
        """
        Basic rule-based sentiment analysis (fallback).
        Uses keyword matching when TextBlob is unavailable.
        """
        text_lower = text.lower()
        
        positive_words = [
            'happy', 'good', 'great', 'excellent', 'wonderful',
            'love', 'like', 'nice', 'awesome', 'amazing',
            'thank', 'thanks', 'please', 'yes', 'ok', 'okay',
            'hello', 'hi', 'hey', 'good morning', 'good afternoon'
        ]
        
        negative_words = [
            'bad', 'terrible', 'awful', 'horrible', 'hate',
            'angry', 'sad', 'wrong', 'error', 'fail', 'failed',
            'no', 'not', 'never', 'stop', 'quit', 'bye'
        ]
        
        pos_count = sum(1 for word in positive_words if word in text_lower)
        neg_count = sum(1 for word in negative_words if word in text_lower)
        
        if pos_count > neg_count:
            category = 'positive'
            polarity = 0.5
        elif neg_count > pos_count:
            category = 'negative'
            polarity = -0.5
        else:
            category = 'neutral'
            polarity = 0.0
        
        return {
            'polarity': polarity,
            'category': category,
            'emoji': self.emoji_map[category]
        }
    
    def get_emoji_for_sentiment(self, category: str) -> str:
        """Get emoji for sentiment category."""
        return self.emoji_map.get(category, self.emoji_map['neutral'])


# Singleton instance
_analyzer = None

def get_analyzer() -> SentimentAnalyzer:
    """Get singleton SentimentAnalyzer instance."""
    global _analyzer
    if _analyzer is None:
        _analyzer = SentimentAnalyzer()
    return _analyzer


if __name__ == "__main__":
    # Test the analyzer
    analyzer = SentimentAnalyzer()
    
    test_messages = [
        "Hello! I'm so happy today!",
        "This is terrible, I hate it.",
        "The weather is okay I guess.",
        "Thank you so much for your help!",
        "I'm feeling neutral about this."
    ]
    
    print("Sentiment Analysis Test:")
    print("-" * 50)
    for msg in test_messages:
        result = analyzer.analyze(msg)
        print(f"Message: {msg}")
        print(f"  Polarity: {result['polarity']}, Category: {result['category']}, Emoji: {result['emoji']}")
        print()
