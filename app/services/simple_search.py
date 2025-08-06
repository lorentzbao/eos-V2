import json
import os
from typing import List, Dict
from janome.tokenizer import Tokenizer
from collections import defaultdict
import math

class SimpleJapaneseSearch:
    def __init__(self, data_file: str = "data/search_index.json"):
        self.data_file = data_file
        self.tokenizer = Tokenizer()
        self.documents = {}
        self.inverted_index = defaultdict(list)
        self.load_data()
    
    def tokenize_japanese(self, text: str) -> List[str]:
        tokens = []
        for token in self.tokenizer.tokenize(text):
            word = token.surface.lower()
            pos = token.part_of_speech.split(',')[0]
            if pos in ['名詞', '動詞', '形容詞', '副詞'] and len(word) > 1:
                tokens.append(word)
        return tokens
    
    def add_document(self, doc_id: str, title: str, content: str, url: str = ""):
        doc = {
            'id': doc_id,
            'title': title,
            'content': content,
            'url': url
        }
        self.documents[doc_id] = doc
        
        # Tokenize and index
        all_text = title + " " + content
        tokens = self.tokenize_japanese(all_text)
        
        # Create term frequency
        term_freq = {}
        for token in tokens:
            term_freq[token] = term_freq.get(token, 0) + 1
        
        # Add to inverted index
        for term, freq in term_freq.items():
            self.inverted_index[term].append({
                'doc_id': doc_id,
                'tf': freq
            })
    
    def add_documents_batch(self, documents: List[Dict]):
        for doc in documents:
            self.add_document(
                doc['id'],
                doc['title'],
                doc['content'],
                doc.get('url', '')
            )
        self.save_data()
    
    def calculate_tfidf(self, term: str, doc_id: str) -> float:
        if term not in self.inverted_index:
            return 0.0
        
        # Find document entry
        doc_entry = None
        for entry in self.inverted_index[term]:
            if entry['doc_id'] == doc_id:
                doc_entry = entry
                break
        
        if not doc_entry:
            return 0.0
        
        tf = doc_entry['tf']
        df = len(self.inverted_index[term])  # document frequency
        total_docs = len(self.documents)
        
        if df == 0 or total_docs == 0:
            return 0.0
        
        idf = math.log(total_docs / df)
        return tf * idf
    
    def search(self, query: str, limit: int = 10) -> List[Dict]:
        query_tokens = self.tokenize_japanese(query)
        if not query_tokens:
            return []
        
        # Calculate scores for each document
        doc_scores = defaultdict(float)
        
        for term in query_tokens:
            if term in self.inverted_index:
                for entry in self.inverted_index[term]:
                    doc_id = entry['doc_id']
                    score = self.calculate_tfidf(term, doc_id)
                    doc_scores[doc_id] += score
        
        # Sort by score and return results
        sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1], reverse=True)
        
        results = []
        for doc_id, score in sorted_docs[:limit]:
            doc = self.documents[doc_id]
            results.append({
                'id': doc_id,
                'title': doc['title'],
                'content': doc['content'][:200] + '...' if len(doc['content']) > 200 else doc['content'],
                'url': doc['url'],
                'score': round(score, 3)
            })
        
        return results
    
    def search_in_title(self, query: str, limit: int = 10) -> List[Dict]:
        query_tokens = self.tokenize_japanese(query)
        if not query_tokens:
            return []
        
        results = []
        for doc_id, doc in self.documents.items():
            title_tokens = self.tokenize_japanese(doc['title'])
            
            # Check if any query token is in title
            score = 0
            for token in query_tokens:
                if token in title_tokens:
                    score += title_tokens.count(token)
            
            if score > 0:
                results.append({
                    'id': doc_id,
                    'title': doc['title'],
                    'content': doc['content'][:200] + '...' if len(doc['content']) > 200 else doc['content'],
                    'url': doc['url'],
                    'score': score
                })
        
        return sorted(results, key=lambda x: x['score'], reverse=True)[:limit]
    
    def get_document_count(self) -> int:
        return len(self.documents)
    
    def save_data(self):
        os.makedirs(os.path.dirname(self.data_file), exist_ok=True)
        data = {
            'documents': self.documents,
            'inverted_index': dict(self.inverted_index)
        }
        with open(self.data_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
    
    def load_data(self):
        if os.path.exists(self.data_file):
            try:
                with open(self.data_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                self.documents = data.get('documents', {})
                self.inverted_index = defaultdict(list, data.get('inverted_index', {}))
            except Exception as e:
                print(f"Error loading data: {e}")
                self.documents = {}
                self.inverted_index = defaultdict(list)