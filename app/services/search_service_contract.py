from typing import List, Dict
from functools import lru_cache
from .whoosh_contract import WhooshContractJapanese
from .query_processor import QueryProcessor

class SearchServiceContract:
    """Search service for contract data with branch and solicitor filtering"""

    def __init__(self, index_dir: str = "data/contract_indexes/A", prewarm: bool = False):
        self.search_engine = WhooshContractJapanese(index_dir, prewarm=prewarm)
        self.query_processor = QueryProcessor()

    @lru_cache(maxsize=128)
    def _cached_search(self, query: str, limit: int, branch_cd: str, solicitor_cd: str,
                      sort_by: str = "", city: str = "") -> tuple:
        """
        Cached search implementation using LRU cache.
        Returns tuple to make it hashable and cacheable.
        """
        processed = self.query_processor.process_advanced_query(query)
        processed_query = processed['processed_query']

        if not processed_query:
            return ([], processed_query)

        try:
            # Contract search with branch and solicitor filtering
            results = self.search_engine.search(query, limit, branch_cd, solicitor_cd, sort_by, city)
            return (results, processed_query)
        except Exception:
            return ([], processed_query)

    def search(self, query: str, limit: int = 10, branch_cd: str = "", solicitor_cd: str = "",
              sort_by: str = "", city: str = "") -> Dict:
        """
        Search contract data with branch and solicitor filtering

        Args:
            query: Search query
            limit: Maximum results
            branch_cd: MOTHERBRANCH_CD filter (支店コード)
            solicitor_cd: SOLICITOR_CD filter (ソリシターコード)
            sort_by: Sort method (revenue, employees)
            city: City filter
        """
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

        # Check cache info before search
        cache_info_before = self._cached_search.cache_info()

        # Use cached search
        try:
            results, processed_query = self._cached_search(query, limit, branch_cd, solicitor_cd, sort_by, city)

            # Check cache info after search to detect hit/miss
            cache_info_after = self._cached_search.cache_info()
            cache_hit = cache_info_after.hits > cache_info_before.hits

            # Group results by company on the Python side
            grouped_results = self._group_by_company(results)

            search_time = time.time() - start_time

            return {
                'grouped_results': grouped_results,
                'total_found': len(results),
                'total_companies': len(grouped_results),
                'query': query,
                'processed_query': processed_query,
                'search_time': round(search_time, 3),
                'cache_hit': cache_hit
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

                    # Contract-specific fields
                    'DISTRICT_NAME': result.get('DISTRICT_NAME', ''),
                    'MOTHERBRANCH_CD': result.get('MOTHERBRANCH_CD', ''),
                    'BRANCH_NAME': result.get('BRANCH_NAME', ''),
                    'SOLICITOR_CD': result.get('SOLICITOR_CD', ''),
                    'SOLICITOR': result.get('SOLICITOR', ''),

                    # Website information
                    'main_domain_url': result.get('main_domain_url', ''),

                    'urls': []
                }

            # Add URL data to the company group
            url_name = result.get('url_name') or result.get('title', '')
            # Truncate url_name to max 50 characters for display
            if len(url_name) > 50:
                url_name = url_name[:50] + '...'

            company_groups[jcn]['urls'].append({
                'url': result.get('url', ''),
                'url_name': url_name,
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
                   DISTRICT_NAME: str = "", MOTHERBRANCH_CD: str = "", BRANCH_NAME: str = "",
                   SOLICITOR_CD: str = "", SOLICITOR: str = "",
                   main_domain_url: str = "", url_name: str = "",
                   content_tokens: str = "") -> bool:
        """Add a single document to the index"""
        doc = {
            'id': doc_id,
            'url': url,
            'content': content,
            'jcn': jcn,
            'CUST_STATUS2': CUST_STATUS2,
            'company_name_kj': company_name_kj,
            'company_address_all': company_address_all,
            'prefecture': prefecture,
            'city': city,
            'LARGE_CLASS_NAME': LARGE_CLASS_NAME,
            'MIDDLE_CLASS_NAME': MIDDLE_CLASS_NAME,
            'CURR_SETLMNT_TAKING_AMT': CURR_SETLMNT_TAKING_AMT,
            'EMPLOYEE_ALL_NUM': EMPLOYEE_ALL_NUM,
            'district_finalized_cd': district_finalized_cd,
            'branch_name_cd': branch_name_cd,
            'DISTRICT_NAME': DISTRICT_NAME,
            'MOTHERBRANCH_CD': MOTHERBRANCH_CD,
            'BRANCH_NAME': BRANCH_NAME,
            'SOLICITOR_CD': SOLICITOR_CD,
            'SOLICITOR': SOLICITOR,
            'main_domain_url': main_domain_url,
            'url_name': url_name,
            'content_tokens': content_tokens
        }
        return self.search_engine.add_documents_batch([doc])

    def add_documents_batch(self, documents: List[Dict]) -> bool:
        """Add multiple documents in a batch"""
        return self.search_engine.add_documents_batch(documents)

    def get_stats(self) -> Dict:
        """Get index statistics"""
        return {
            'total_documents': self.search_engine.get_document_count(),
            'index_dir': self.search_engine.index_dir
        }

    def clear_index(self):
        """Clear all documents from the index"""
        self.search_engine.clear_index()
        # Clear cache when index is cleared
        self._cached_search.cache_clear()

    def optimize_index(self):
        """Optimize the index for better performance"""
        self.search_engine.optimize_index()
