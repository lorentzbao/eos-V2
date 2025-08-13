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
    
    def get_user_searches(self, username: str, limit: int = 10) -> List[Dict]:
        """Get search history for a specific user - optimized for large files"""
        searches = []
        
        try:
            if not os.path.exists(self.log_file):
                return searches
            
            # Use reverse file reading for better performance on large files
            searches = self._read_user_logs_reverse(username, limit)
            
        except Exception as e:
            print(f"Failed to get user searches: {e}")
            return []
        
        return searches
    
    def _read_user_logs_reverse(self, username: str, limit: int) -> List[Dict]:
        """Read user logs in reverse order for efficiency"""
        user_searches = []
        
        try:
            # Read file in reverse order using seek
            with open(self.log_file, 'rb') as f:
                f.seek(0, 2)  # Go to end of file
                file_size = f.tell()
                
                # Read file in chunks from the end
                chunk_size = 8192
                lines = []
                position = file_size
                
                while position > 0 and len(user_searches) < limit:
                    # Calculate chunk start position
                    chunk_start = max(0, position - chunk_size)
                    chunk_length = position - chunk_start
                    
                    # Read chunk
                    f.seek(chunk_start)
                    chunk = f.read(chunk_length).decode('utf-8', errors='ignore')
                    
                    # Split into lines and reverse
                    chunk_lines = chunk.split('\n')
                    
                    # If we're not at the beginning, the first line might be incomplete
                    if chunk_start > 0 and chunk_lines:
                        chunk_lines = chunk_lines[1:]
                    
                    # Process lines in reverse order
                    for line in reversed(chunk_lines):
                        if line.strip():
                            try:
                                entry = json.loads(line.strip())
                                if entry.get('username') == username:
                                    user_searches.append(entry)
                                    if len(user_searches) >= limit:
                                        break
                            except json.JSONDecodeError:
                                continue
                    
                    position = chunk_start
                
        except Exception as e:
            print(f"Error reading logs in reverse: {e}")
            # Fallback to original method
            return self._read_user_logs_fallback(username, limit)
        
        return user_searches
    
    def _read_user_logs_fallback(self, username: str, limit: int) -> List[Dict]:
        """Fallback method for reading user logs"""
        searches = []
        
        try:
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
            print(f"Fallback method failed: {e}")
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