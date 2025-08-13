from typing import List, Dict, Optional
from .whoosh_simple import WhooshSimpleJapanese
from .query_processor import QueryProcessor

class SearchService:
    def __init__(self, index_dir: str = "data/whoosh_index"):
        self.search_engine = WhooshSimpleJapanese(index_dir)
        self.query_processor = QueryProcessor()
    
    def search(self, query: str, limit: int = 10, search_type: str = "auto", prefecture: str = "") -> Dict:
        if not query.strip():
            return {
                'results': [],
                'total_found': 0,
                'query': query,
                'processed_query': '',
                'search_time': 0
            }
        
        import time
        start_time = time.time()
        
        processed = self.query_processor.process_advanced_query(query)
        processed_query = processed['processed_query']
        
        if not processed_query:
            return {
                'results': [],
                'total_found': 0,
                'query': query,
                'processed_query': processed_query,
                'search_time': 0
            }
        
        try:
            if search_type == "title" or processed['search_type'] == 'title':
                results = self.search_engine.search_in_title(query, limit, prefecture)
            else:
                results = self.search_engine.search(query, limit, prefecture)
            
            search_time = time.time() - start_time
            
            return {
                'results': results,
                'total_found': len(results),
                'query': query,
                'processed_query': processed_query,
                'search_time': round(search_time, 3)
            }
        
        except Exception as e:
            return {
                'results': [],
                'total_found': 0,
                'query': query,
                'processed_query': processed_query,
                'search_time': 0,
                'error': str(e)
            }
    
    def add_document(self, doc_id: str, title: str, content: str, introduction: str, url: str = "", prefecture: str = ""):
        return self.search_engine.add_document(doc_id, title, content, introduction, url, prefecture)
    
    def add_documents_batch(self, documents: List[Dict]):
        return self.search_engine.add_documents_batch(documents)
    
    def get_stats(self) -> Dict:
        return {
            'total_documents': self.search_engine.get_document_count(),
            'engine_type': 'Whoosh'
        }
    
    def clear_index(self):
        """Clear the search index (Whoosh-specific)"""
        return self.search_engine.clear_index()
    
    def optimize_index(self):
        """Optimize the search index (Whoosh-specific)"""
        return self.search_engine.optimize_index()