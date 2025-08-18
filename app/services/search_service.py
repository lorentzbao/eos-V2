from typing import List, Dict, Optional
from functools import lru_cache
from .whoosh_simple import WhooshSimpleJapanese
from .query_processor import QueryProcessor

class SearchService:
    def __init__(self, index_dir: str = "data/whoosh_index"):
        self.search_engine = WhooshSimpleJapanese(index_dir)
        self.query_processor = QueryProcessor()
    
    @lru_cache(maxsize=128)
    def _cached_search(self, query: str, limit: int, search_type: str, prefecture: str, sort_by: str = "") -> tuple:
        """
        Cached search implementation using LRU cache.
        Returns tuple to make it hashable and cacheable.
        """
        processed = self.query_processor.process_advanced_query(query)
        processed_query = processed['processed_query']
        
        if not processed_query:
            return ([], processed_query)
        
        try:
            if search_type == "title" or processed['search_type'] == 'title':
                results = self.search_engine.search_in_title(query, limit, prefecture)
            else:
                results = self.search_engine.search(query, limit, prefecture, sort_by)
            
            return (results, processed_query)
        except Exception:
            return ([], processed_query)
    
    def search(self, query: str, limit: int = 10, search_type: str = "auto", prefecture: str = "", sort_by: str = "") -> Dict:
        if not query.strip():
            return {
                'results': [],
                'grouped_results': [],
                'total_found': 0,
                'query': query,
                'processed_query': '',
                'search_time': 0
            }
        
        import time
        start_time = time.time()
        
        # Use cached search
        try:
            results, processed_query = self._cached_search(query, limit, search_type, prefecture, sort_by)
            
            # Group results by company on the Python side
            grouped_results = self._group_by_company(results)
            
            search_time = time.time() - start_time
            
            return {
                'results': results,  # Keep original for backward compatibility
                'grouped_results': grouped_results,  # New grouped structure
                'total_found': len(results),
                'total_companies': len(grouped_results),
                'query': query,
                'processed_query': processed_query,
                'search_time': round(search_time, 3)
            }
        
        except Exception as e:
            return {
                'results': [],
                'grouped_results': [],
                'total_found': 0,
                'total_companies': 0,
                'query': query,
                'processed_query': '',
                'search_time': 0,
                'error': str(e)
            }
    
    def _group_by_company(self, results: List[Dict]) -> List[Dict]:
        """
        Group search results by company_number for better performance
        Returns a list of company objects with nested URLs
        """
        if not results:
            return []
        
        company_groups = {}
        
        for result in results:
            company_number = result.get('company_number') or result.get('id', 'unknown')
            company_name = result.get('company_name') or result.get('title', 'Unknown Company')
            
            if company_number not in company_groups:
                company_groups[company_number] = {
                    'company_name': company_name,
                    'company_number': company_number,
                    'company_tel': result.get('company_tel', ''),
                    'company_industry': result.get('company_industry', ''),
                    'prefecture': result.get('prefecture', ''),
                    'urls': []
                }
            
            # Add URL data to the company group
            company_groups[company_number]['urls'].append({
                'url': result.get('url', ''),
                'url_name': result.get('url_name') or result.get('title', ''),
                'content': result.get('content') or result.get('introduction', ''),
                'matched_terms': result.get('matched_terms', []),
                'score': result.get('score', 0),
                'id': result.get('id', '')
            })
        
        # Convert to list and sort by company_number for consistent ordering
        grouped_companies = list(company_groups.values())
        grouped_companies.sort(key=lambda x: x['company_number'])
        
        return grouped_companies
    
    def add_document(self, doc_id: str, title: str, content: str, introduction: str, url: str = "", prefecture: str = ""):
        result = self.search_engine.add_document(doc_id, title, content, introduction, url, prefecture)
        # Clear cache when documents are added
        self._cached_search.cache_clear()
        return result
    
    def add_documents_batch(self, documents: List[Dict]):
        result = self.search_engine.add_documents_batch(documents)
        # Clear cache when documents are added
        self._cached_search.cache_clear()
        return result
    
    def get_stats(self) -> Dict:
        # Get cache info
        cache_info = self._cached_search.cache_info()
        
        return {
            'total_documents': self.search_engine.get_document_count(),
            'engine_type': 'Whoosh',
            'cache_hits': cache_info.hits,
            'cache_misses': cache_info.misses,
            'cache_size': cache_info.currsize,
            'cache_max_size': cache_info.maxsize
        }
    
    def clear_index(self):
        """Clear the search index (Whoosh-specific)"""
        result = self.search_engine.clear_index()
        # Clear cache when index is cleared
        self._cached_search.cache_clear()
        return result
    
    def optimize_index(self):
        """Optimize the search index (Whoosh-specific)"""
        return self.search_engine.optimize_index()
    
    def clear_cache(self):
        """Manually clear the search cache"""
        self._cached_search.cache_clear()
        
    def get_cache_info(self):
        """Get detailed cache information"""
        return self._cached_search.cache_info()
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID"""
        result = self.search_engine.delete_document(doc_id)
        # Clear cache when documents are deleted
        self._cached_search.cache_clear()
        return result