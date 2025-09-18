import re
from typing import Dict, List, Optional
from janome.tokenizer import Tokenizer

class QueryProcessor:
    def __init__(self):
        self.tokenizer = Tokenizer()
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
        tokens = []
        for token in self.tokenizer.tokenize(text):
            word = token.surface
            pos = token.part_of_speech.split(',')[0]
            if pos in ['名詞', '動詞', '形容詞', '副詞'] and len(word) > 1:
                tokens.append(word)
        return tokens
    
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