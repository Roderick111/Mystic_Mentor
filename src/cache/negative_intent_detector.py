#!/usr/bin/env python3
"""
Negative Intent Detection for Lunar Cache System
Prevents inappropriate responses to negative queries
"""

from typing import List, Set


class NegativeIntentDetector:
    """Detects negative intent in user queries to prevent inappropriate responses"""
    
    # Comprehensive negative intent words
    NEGATIVE_WORDS: Set[str] = {
        'avoid', 'dangerous', 'harmful', "don't", 'stop', 'fail', 'bad', 'wrong',
        'against', 'not', 'never', 'cant', "can't", 'shouldnt', "shouldn't",
        'dispose', 'get rid', 'remove', 'toxic', 'unsafe', 'risky', 'problem',
        'issue', 'concern', 'warning', 'caution', 'why not', 'dont', 'wont',
        "won't", 'refuse', 'reject', 'oppose', 'prevent', 'block', 'forbidden'
    }
    
    # Additional negative phrases (more context-sensitive)
    NEGATIVE_PHRASES: Set[str] = {
        'why should i avoid', 'is it dangerous', 'why not to', 'problems with',
        'issues with', 'side effects', 'negative effects', 'what not to',
        'when not to', 'how to stop', 'how to avoid', 'why avoid'
    }
    
    def __init__(self, sensitivity: float = 0.85):
        """
        Initialize negative intent detector
        
        Args:
            sensitivity: Threshold for negative intent detection (0.0-1.0)
        """
        self.sensitivity = sensitivity
        self.negative_word_threshold = 0.90 if sensitivity >= 0.85 else 0.85
    
    def has_negative_intent(self, query: str) -> bool:
        """
        Check if query contains negative intent
        
        Args:
            query: User query to analyze
            
        Returns:
            True if negative intent detected, False otherwise
        """
        if not query or not query.strip():
            return False
        
        query_lower = query.lower().strip()
        
        # Check for negative phrases first (most specific)
        if self._contains_negative_phrases(query_lower):
            return True
        
        # Check for negative words (broader detection)
        if self._contains_negative_words(query_lower):
            return True
        
        return False
    
    def _contains_negative_phrases(self, query_lower: str) -> bool:
        """Check for specific negative phrases"""
        return any(phrase in query_lower for phrase in self.NEGATIVE_PHRASES)
    
    def _contains_negative_words(self, query_lower: str) -> bool:
        """Check for negative words with context awareness"""
        words_in_query = set(query_lower.split())
        
        # Direct negative word matches
        negative_matches = words_in_query.intersection(self.NEGATIVE_WORDS)
        
        if not negative_matches:
            return False
        
        # Context-aware filtering
        # If query is very short and contains negative words, likely negative intent
        if len(words_in_query) <= 5 and negative_matches:
            return True
        
        # If multiple negative words, likely negative intent
        if len(negative_matches) >= 2:
            return True
        
        # Single negative word in longer query - use threshold
        negative_ratio = len(negative_matches) / len(words_in_query)
        return negative_ratio >= (1.0 - self.sensitivity)
    
    def get_negative_indicators(self, query: str) -> List[str]:
        """
        Get list of negative indicators found in query (for debugging)
        
        Args:
            query: User query to analyze
            
        Returns:
            List of negative words/phrases found
        """
        if not query:
            return []
        
        query_lower = query.lower().strip()
        indicators = []
        
        # Find negative phrases
        for phrase in self.NEGATIVE_PHRASES:
            if phrase in query_lower:
                indicators.append(f"phrase: '{phrase}'")
        
        # Find negative words
        words_in_query = set(query_lower.split())
        negative_words = words_in_query.intersection(self.NEGATIVE_WORDS)
        for word in negative_words:
            indicators.append(f"word: '{word}'")
        
        return indicators
    
    def get_stats(self) -> dict:
        """Get statistics about the negative intent detector"""
        return {
            'negative_words_count': len(self.NEGATIVE_WORDS),
            'negative_phrases_count': len(self.NEGATIVE_PHRASES),
            'sensitivity': self.sensitivity,
            'negative_word_threshold': self.negative_word_threshold
        } 