from typing import List, Dict
from functools import lru_cache
from .whoosh_simple import WhooshSimpleJapanese
from .query_processor import QueryProcessor

class SearchService:
    def __init__(self, index_dir: str = "data/whoosh_index"):
        self.search_engine = WhooshSimpleJapanese(index_dir)
        self.query_processor = QueryProcessor()
    
    @lru_cache(maxsize=128)
    def _cached_search(self, query: str, limit: int, prefecture: str, cust_status: str, sort_by: str = "") -> tuple:
        """
        Cached search implementation using LRU cache.
        Returns tuple to make it hashable and cacheable.
        """
        processed = self.query_processor.process_advanced_query(query)
        processed_query = processed['processed_query']
        
        if not processed_query:
            return ([], processed_query)
        
        try:
            # Only content search is available now with prefecture and cust_status filtering
            results = self.search_engine.search(query, limit, prefecture, cust_status, sort_by)
            return (results, processed_query)
        except Exception:
            return ([], processed_query)
    
    def search(self, query: str, limit: int = 10, prefecture: str = "", cust_status: str = "", sort_by: str = "") -> Dict:
        if not query.strip():
            return {
                'grouped_results': [],
                'total_found': 0,
                'total_companies': 0,
                'query': query,
                'processed_query': '',
                'search_time': 0
            }
        
        import time
        start_time = time.time()
        
        # Use cached search
        try:
            results, processed_query = self._cached_search(query, limit, prefecture, cust_status, sort_by)
            
            # Group results by company on the Python side
            grouped_results = self._group_by_company(results)
            
            search_time = time.time() - start_time
            
            return {
                'grouped_results': grouped_results,
                'total_found': len(results),
                'total_companies': len(grouped_results),
                'query': query,
                'processed_query': processed_query,
                'search_time': round(search_time, 3)
            }
        
        except Exception as e:
            return {
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
        Group search results by JCN (法人番号) for enterprise data
        Returns a list of company objects with comprehensive corporate info and nested URLs
        """
        if not results:
            return []
        
        company_groups = {}
        
        for result in results:
            # Use JCN as primary key for company grouping
            jcn = result.get('jcn', 'unknown')
            company_name = result.get('company_name_kj', 'Unknown Company')
            
            if jcn not in company_groups:
                company_groups[jcn] = {
                    # Corporate identification
                    'jcn': jcn,
                    'company_name_kj': company_name,
                    'CUST_STATUS2': result.get('CUST_STATUS2', ''),
                    
                    # Address information
                    'company_address_all': result.get('company_address_all', ''),
                    'prefecture': result.get('prefecture', ''),
                    'city': result.get('city', ''),
                    
                    # Industry classification
                    'LARGE_CLASS_NAME': result.get('LARGE_CLASS_NAME', ''),
                    'MIDDLE_CLASS_NAME': result.get('MIDDLE_CLASS_NAME', ''),
                    
                    # Financial data
                    'CURR_SETLMNT_TAKING_AMT': result.get('CURR_SETLMNT_TAKING_AMT', ''),
                    'EMPLOYEE_ALL_NUM': result.get('EMPLOYEE_ALL_NUM', ''),
                    
                    # Organization codes
                    'district_finalized_cd': result.get('district_finalized_cd', ''),
                    'branch_name_cd': result.get('branch_name_cd', ''),
                    
                    # Website information
                    'main_domain_url': result.get('main_domain_url', ''),
                    
                    'urls': []
                }
            
            # Add URL data to the company group
            company_groups[jcn]['urls'].append({
                'url': result.get('url', ''),
                'url_name': result.get('url_name') or result.get('title', ''),
                'content': result.get('content') or result.get('introduction', ''),
                'matched_terms': result.get('matched_terms', []),
                'score': result.get('score', 0),
                'id': result.get('id', '')
            })
        
        # Convert to list and sort by JCN for consistent ordering
        grouped_companies = list(company_groups.values())
        grouped_companies.sort(key=lambda x: x['jcn'])
        
        return grouped_companies
    
    def add_document(self, doc_id: str, url: str = "", content: str = "", 
                   jcn: str = "", CUST_STATUS2: str = "", company_name_kj: str = "",
                   company_address_all: str = "", prefecture: str = "", city: str = "",
                   LARGE_CLASS_NAME: str = "", MIDDLE_CLASS_NAME: str = "",
                   CURR_SETLMNT_TAKING_AMT: int = 0, EMPLOYEE_ALL_NUM: int = 0,
                   district_finalized_cd: str = "", branch_name_cd: str = "",
                   main_domain_url: str = "", url_name: str = ""):
        result = self.search_engine.add_document(
            doc_id, url, content, jcn, CUST_STATUS2, company_name_kj,
            company_address_all, prefecture, city, LARGE_CLASS_NAME, 
            MIDDLE_CLASS_NAME, CURR_SETLMNT_TAKING_AMT, EMPLOYEE_ALL_NUM,
            district_finalized_cd, branch_name_cd, main_domain_url, url_name
        )
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