from typing import Dict, List
from functools import lru_cache
from .search_service import SearchService
from omegaconf import DictConfig

class MultiIndexSearchService:
    """Search service that manages multiple prefecture-based indexes"""
    
    def __init__(self, indexes_config: DictConfig):
        self.indexes_config = indexes_config
        self.search_services = {}
        
        # Initialize search service for each prefecture
        for prefecture, config in indexes_config.items():
            # Handle both DictConfig and regular dict
            index_dir = config.dir if hasattr(config, 'dir') else config['dir']
            self.search_services[prefecture] = SearchService(index_dir)
    
    def get_available_prefectures(self) -> List[Dict]:
        """Get list of available prefectures for frontend selection"""
        prefectures = []
        for prefecture, config in self.indexes_config.items():
            # Handle both DictConfig and regular dict
            name = config.name if hasattr(config, 'name') else config['name']
            index_dir = config.dir if hasattr(config, 'dir') else config['dir']
            prefectures.append({
                'value': prefecture,
                'name': name,
                'index_dir': index_dir
            })
        return prefectures
    
    def search(self, query: str, prefecture: str, limit: int = 10, 
               cust_status: str = "", sort_by: str = "") -> Dict:
        """
        Search in a specific prefecture index
        
        Args:
            query: Search query
            prefecture: Required prefecture (tokyo, osaka, etc.)
            limit: Maximum results
            cust_status: Customer status filter
            sort_by: Sort method
        """
        if not prefecture:
            return {
                'grouped_results': [],
                'total_found': 0,
                'total_companies': 0,
                'query': query,
                'processed_query': '',
                'search_time': 0,
                'error': 'Prefecture selection is required'
            }
        
        if prefecture not in self.search_services:
            return {
                'grouped_results': [],
                'total_found': 0,
                'total_companies': 0,
                'query': query,
                'processed_query': '',
                'search_time': 0,
                'error': f'Prefecture "{prefecture}" not available'
            }
        
        # Search in the specific prefecture index
        service = self.search_services[prefecture]
        results = service.search(query, limit, "", cust_status, sort_by)  # prefecture="" since it's already filtered
        
        # Add prefecture info to results
        results['prefecture'] = prefecture
        config = self.indexes_config[prefecture]
        name = config.name if hasattr(config, 'name') else config['name']
        results['prefecture_name'] = name
        
        return results
    
    def get_stats(self, prefecture: str = None) -> Dict:
        """Get statistics for a specific prefecture or all prefectures"""
        if prefecture:
            if prefecture in self.search_services:
                stats = self.search_services[prefecture].get_stats()
                stats['prefecture'] = prefecture
                config = self.indexes_config[prefecture]
                name = config.name if hasattr(config, 'name') else config['name']
                stats['prefecture_name'] = name
                return stats
            else:
                return {'error': f'Prefecture "{prefecture}" not available'}
        
        # Get stats for all prefectures
        all_stats = {
            'prefectures': {},
            'total_documents': 0,
            'available_prefectures': self.get_available_prefectures()
        }
        
        for pref, service in self.search_services.items():
            pref_stats = service.get_stats()
            config = self.indexes_config[pref]
            name = config.name if hasattr(config, 'name') else config['name']
            all_stats['prefectures'][pref] = {
                'name': name,
                'stats': pref_stats
            }
            all_stats['total_documents'] += pref_stats['total_documents']
        
        return all_stats
    
    def add_document(self, prefecture: str, **kwargs):
        """Add document to specific prefecture index"""
        if prefecture not in self.search_services:
            return False
        return self.search_services[prefecture].add_document(**kwargs)
    
    def add_documents_batch(self, prefecture: str, documents: List[Dict]):
        """Add documents batch to specific prefecture index"""
        if prefecture not in self.search_services:
            return False
        return self.search_services[prefecture].add_documents_batch(documents)
    
    def clear_index(self, prefecture: str):
        """Clear specific prefecture index"""
        if prefecture not in self.search_services:
            return False
        return self.search_services[prefecture].clear_index()
    
    def optimize_index(self, prefecture: str):
        """Optimize specific prefecture index"""
        if prefecture not in self.search_services:
            return False
        return self.search_services[prefecture].optimize_index()