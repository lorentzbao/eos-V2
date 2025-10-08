import re
from typing import Dict, List, Optional
from .tokenizers import get_tokenizer

class QueryProcessor:
    def __init__(self, tokenizer_type: Optional[str] = None):
        """
        Initialize QueryProcessor with a Japanese tokenizer.

        Args:
            tokenizer_type: Type of tokenizer ('janome', 'mecab', or None for auto-detect)
        """
        self.tokenizer = get_tokenizer(tokenizer_type)
        self.operators = ['AND', 'OR', 'NOT', '+', '-', '"']
    
    def normalize_query(self, query: str) -> str:
        query = query.strip()
        # Convert full-width space to half-width space
        query = query.replace('　', ' ')
        query = re.sub(r'\s+', ' ', query)
        return query
    
    def extract_quoted_phrases(self, query: str) -> tuple:
        phrases = re.findall(r'"([^"]*)"', query)
        clean_query = re.sub(r'"[^"]*"', '', query).strip()
        return clean_query, phrases
    
    def tokenize_japanese(self, text: str) -> List[str]:
        """Tokenize Japanese text with POS filtering"""
        return self.tokenizer.tokenize_and_filter(text, min_length=2)
    
    def build_whoosh_query(self, query: str) -> str:
        query = self.normalize_query(query)
        
        clean_query, phrases = self.extract_quoted_phrases(query)
        
        if phrases:
            phrase_parts = [f'"{phrase}"' for phrase in phrases if phrase.strip()]
        else:
            phrase_parts = []
        
        if clean_query:
            tokens = self.tokenize_japanese(clean_query)
            token_parts = [f'({token})' for token in tokens if token]
        else:
            token_parts = []
        
        all_parts = phrase_parts + token_parts
        
        if not all_parts:
            return ""
        
        return ' '.join(all_parts)
    
    def process_advanced_query(self, query: str) -> Dict:
        result = {
            'processed_query': '',
            'filters': {}
        }
        
        query = self.normalize_query(query)
        
        result['processed_query'] = self.build_whoosh_query(query)
        
        return result