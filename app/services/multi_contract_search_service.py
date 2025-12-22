from typing import Dict, List
from .search_service_contract import SearchServiceContract
from omegaconf import DictConfig

class MultiContractSearchService:
    """Search service that manages multiple district-based contract indexes"""

    def __init__(self, indexes_config: DictConfig, prewarm: bool = False):
        self.indexes_config = indexes_config
        self.search_services = {}

        # Initialize search service for each district
        for district, config in indexes_config.items():
            # Handle both DictConfig and regular dict
            index_dir = config.dir if hasattr(config, 'dir') else config['dir']
            self.search_services[district] = SearchServiceContract(index_dir, prewarm=prewarm)

    def get_available_districts(self) -> List[Dict]:
        """Get list of available districts for frontend selection, sorted by district code"""
        districts = []
        for district, config in self.indexes_config.items():
            # Handle both DictConfig and regular dict
            name = config.name if hasattr(config, 'name') else config['name']
            index_dir = config.dir if hasattr(config, 'dir') else config['dir']
            district_cd = config.district_cd if hasattr(config, 'district_cd') else config.get('district_cd', district)
            districts.append({
                'value': district,
                'name': name,
                'index_dir': index_dir,
                'district_cd': district_cd
            })
        # Sort by district code
        districts.sort(key=lambda x: x['district_cd'])
        return districts

    def search(self, query: str, district: str, limit: int = 10,
               branch_cd: str = "", solicitor_cd: str = "", sort_by: str = "", city: str = "") -> Dict:
        """
        Search in a specific district index with branch and solicitor filtering

        Args:
            query: Search query
            district: Required district (A, B, C, ...)
            limit: Maximum results
            branch_cd: MOTHERBRANCH_CD filter (支店コード)
            solicitor_cd: SOLICITOR_CD filter (ソリシターコード)
            sort_by: Sort method
            city: City filter
        """
        if not district:
            return {
                'grouped_results': [],
                'total_found': 0,
                'total_companies': 0,
                'query': query,
                'processed_query': '',
                'search_time': 0,
                'error': 'District selection is required'
            }

        if district not in self.search_services:
            return {
                'grouped_results': [],
                'total_found': 0,
                'total_companies': 0,
                'query': query,
                'processed_query': '',
                'search_time': 0,
                'error': f'District "{district}" not available'
            }

        # Search in the specific district index
        service = self.search_services[district]
        results = service.search(query, limit, branch_cd, solicitor_cd, sort_by, city)

        # Add district info to results
        results['district'] = district
        config = self.indexes_config[district]
        name = config.name if hasattr(config, 'name') else config['name']
        results['district_name'] = name

        return results

    def get_stats(self, district: str = None) -> Dict:
        """Get statistics for a specific district or all districts"""
        if district:
            if district in self.search_services:
                stats = self.search_services[district].get_stats()
                stats['district'] = district
                config = self.indexes_config[district]
                name = config.name if hasattr(config, 'name') else config['name']
                stats['district_name'] = name
                return stats
            else:
                return {'error': f'District "{district}" not available'}

        # Get stats for all districts
        all_stats = {
            'districts': {},
            'total_documents': 0,
            'available_districts': self.get_available_districts()
        }

        for dist, service in self.search_services.items():
            dist_stats = service.get_stats()
            config = self.indexes_config[dist]
            name = config.name if hasattr(config, 'name') else config['name']
            all_stats['districts'][dist] = {
                'name': name,
                'stats': dist_stats
            }
            all_stats['total_documents'] += dist_stats['total_documents']

        return all_stats

    def add_document(self, district: str, **kwargs):
        """Add document to specific district index"""
        if district not in self.search_services:
            return False
        return self.search_services[district].add_document(**kwargs)

    def add_documents_batch(self, district: str, documents: List[Dict]):
        """Add documents batch to specific district index"""
        if district not in self.search_services:
            return False
        return self.search_services[district].add_documents_batch(documents)

    def clear_index(self, district: str):
        """Clear specific district index"""
        if district not in self.search_services:
            return False
        return self.search_services[district].clear_index()

    def optimize_index(self, district: str):
        """Optimize specific district index"""
        if district not in self.search_services:
            return False
        return self.search_services[district].optimize_index()
