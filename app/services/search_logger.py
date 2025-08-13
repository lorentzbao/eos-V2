import os
import json
import datetime
from typing import List, Dict

class SearchLogger:
    """Log and track user search queries"""
    
    def __init__(self, log_file="data/search_logs.jsonl"):
        self.log_file = log_file
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """Create log directory if it doesn't exist"""
        os.makedirs(os.path.dirname(self.log_file), exist_ok=True)
    
    def log_search(self, username: str, query: str, search_type: str = "auto", 
                   results_count: int = 0, search_time: float = 0.0):
        """Log a search query by user with detailed information"""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "username": username,
            "query": query,
            "search_type": search_type,
            "results_count": results_count,
            "search_time": round(search_time, 3)
        }
        
        try:
            with open(self.log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
        except Exception as e:
            print(f"Failed to log search: {e}")
    
    def get_user_searches(self, username: str, limit: int = 100) -> List[Dict]:
        """Get search history for a specific user"""
        searches = []
        
        try:
            if not os.path.exists(self.log_file):
                return searches
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        if entry.get('username') == username:
                            searches.append(entry)
                    except json.JSONDecodeError:
                        continue
            
            # Return most recent searches first
            searches.sort(key=lambda x: x['timestamp'], reverse=True)
            return searches[:limit]
            
        except Exception as e:
            print(f"Failed to get user searches: {e}")
            return []
    
    def get_all_searches(self, limit: int = 500) -> List[Dict]:
        """Get all search logs (for admin purposes)"""
        searches = []
        
        try:
            if not os.path.exists(self.log_file):
                return searches
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        searches.append(entry)
                    except json.JSONDecodeError:
                        continue
            
            # Return most recent searches first
            searches.sort(key=lambda x: x['timestamp'], reverse=True)
            return searches[:limit]
            
        except Exception as e:
            print(f"Failed to get all searches: {e}")
            return []
    
    def get_popular_queries(self, limit: int = 10) -> List[Dict]:
        """Get most popular search queries across all users"""
        query_counts = {}
        
        try:
            if not os.path.exists(self.log_file):
                return []
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        query = entry.get('query', '').strip().lower()
                        if query:
                            query_counts[query] = query_counts.get(query, 0) + 1
                    except json.JSONDecodeError:
                        continue
            
            # Sort by count and return top queries
            popular = sorted(query_counts.items(), key=lambda x: x[1], reverse=True)
            return [{"query": query, "count": count} for query, count in popular[:limit]]
            
        except Exception as e:
            print(f"Failed to get popular queries: {e}")
            return []
    
    def get_user_stats(self) -> Dict:
        """Get statistics about users and searches"""
        stats = {
            "total_searches": 0,
            "unique_users": set(),
            "unique_queries": set()
        }
        
        try:
            if not os.path.exists(self.log_file):
                return {
                    "total_searches": 0,
                    "unique_users": 0,
                    "unique_queries": 0
                }
            
            with open(self.log_file, 'r', encoding='utf-8') as f:
                for line in f:
                    try:
                        entry = json.loads(line.strip())
                        stats["total_searches"] += 1
                        stats["unique_users"].add(entry.get('username', ''))
                        stats["unique_queries"].add(entry.get('query', '').strip().lower())
                    except json.JSONDecodeError:
                        continue
            
            return {
                "total_searches": stats["total_searches"],
                "unique_users": len(stats["unique_users"]),
                "unique_queries": len(stats["unique_queries"])
            }
            
        except Exception as e:
            print(f"Failed to get user stats: {e}")
            return {
                "total_searches": 0,
                "unique_users": 0,
                "unique_queries": 0
            }