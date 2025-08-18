import os
import json
import datetime
from typing import List, Dict
import glob
import threading
from collections import defaultdict
from .query_processor import QueryProcessor

class SearchLogger:
    """Log and track user search queries using per-user log files"""
    
    def __init__(self, log_dir="data/search_logs"):
        self.log_dir = log_dir
        self.query_processor = QueryProcessor()
        self._ensure_log_directory()
        
        # In-memory ranking tracker
        self._query_counts = defaultdict(int)
        self._rankings_lock = threading.RLock()
        
        # Initialize rankings from existing logs on startup
        self._initialize_rankings()
    
    def _ensure_log_directory(self):
        """Create log directory if it doesn't exist"""
        os.makedirs(self.log_dir, exist_ok=True)
    
    def _get_user_log_file(self, username: str) -> str:
        """Get the log file path for a specific user"""
        # Sanitize username for safe filename
        safe_username = "".join(c for c in username if c.isalnum() or c in "_-.")
        return os.path.join(self.log_dir, f"{safe_username}.jsonl")
    
    def _initialize_rankings(self):
        """Initialize in-memory rankings from existing log files on startup"""
        print("Initializing search rankings from existing logs...")
        
        try:
            user_files = glob.glob(os.path.join(self.log_dir, "*.jsonl"))
            total_queries_loaded = 0
            
            with self._rankings_lock:
                for user_file in user_files:
                    with open(user_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                entry = json.loads(line.strip())
                                query = entry.get('query', '')
                                # Normalize query for consistent ranking
                                normalized_query = self.query_processor.normalize_query(query).lower()
                                if normalized_query:
                                    self._query_counts[normalized_query] += 1
                                    total_queries_loaded += 1
                            except json.JSONDecodeError:
                                continue
                
            print(f"Loaded {total_queries_loaded} queries into rankings ({len(self._query_counts)} unique)")
            
        except Exception as e:
            print(f"Error initializing rankings: {e}")
            # Continue with empty rankings
            self._query_counts = defaultdict(int)
    
    def log_search(self, username: str, query: str, search_type: str = "auto", 
                   results_count: int = 0, search_time: float = 0.0, prefecture: str = ""):
        """Log a search query by user with detailed information"""
        # Normalize query for consistent tracking
        normalized_query = self.query_processor.normalize_query(query)
        
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "query": normalized_query,
            "search_type": search_type,
            "results_count": results_count,
            "search_time": round(search_time, 3)
        }
        
        # Only include prefecture if it's specified
        if prefecture:
            log_entry["prefecture"] = prefecture
        
        try:
            # Write to file
            user_log_file = self._get_user_log_file(username)
            with open(user_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
                
            # Update in-memory rankings in real-time
            query_key = normalized_query.strip().lower()
            if query_key:
                with self._rankings_lock:
                    self._query_counts[query_key] += 1
                    
        except Exception as e:
            print(f"Failed to log search for {username}: {e}")
    
    def get_user_searches(self, username: str, limit: int = 10) -> List[Dict]:
        """Get search history for a specific user - O(log n + k) complexity"""
        searches = []
        
        try:
            user_log_file = self._get_user_log_file(username)
            if not os.path.exists(user_log_file):
                return searches
            
            # Read the user's specific log file and get recent entries
            searches = self._read_user_file_reverse(user_log_file, limit)
            
        except Exception as e:
            print(f"Failed to get user searches for {username}: {e}")
            return []
        
        return searches
    
    def _read_user_file_reverse(self, user_log_file: str, limit: int) -> List[Dict]:
        """Read user's log file in reverse order for efficiency"""
        user_searches = []
        
        try:
            # Read file in reverse order using seek
            with open(user_log_file, 'rb') as f:
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
                                # No need to filter by username since this is already a per-user file
                                user_searches.append(entry)
                                if len(user_searches) >= limit:
                                    break
                            except json.JSONDecodeError:
                                continue
                    
                    position = chunk_start
                
        except Exception as e:
            print(f"Error reading user file in reverse: {e}")
            # Fallback to simple method for per-user file
            return self._read_user_file_simple(user_log_file, limit)
        
        return user_searches
    
    def _read_user_file_simple(self, user_log_file: str, limit: int) -> List[Dict]:
        """Simple fallback method for reading user's log file"""
        searches = []
        
        try:
            with open(user_log_file, 'r', encoding='utf-8') as f:
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
            print(f"Simple fallback method failed: {e}")
            return []
    
    def get_all_searches(self, limit: int = 500) -> List[Dict]:
        """Get all search logs across all users (for admin purposes)"""
        searches = []
        
        try:
            # Get all user log files
            user_files = glob.glob(os.path.join(self.log_dir, "*.jsonl"))
            
            for user_file in user_files:
                username = os.path.basename(user_file).replace('.jsonl', '')
                
                with open(user_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            # Add username back to entry for admin purposes
                            entry['username'] = username
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
        """Get most popular search queries across all users (real-time from memory)"""
        try:
            with self._rankings_lock:
                # Sort by count and return top queries
                popular = sorted(self._query_counts.items(), key=lambda x: x[1], reverse=True)
                return [{"query": query, "count": count} for query, count in popular[:limit]]
                
        except Exception as e:
            print(f"Failed to get popular queries: {e}")
            return []
    
    def get_rankings_stats(self) -> Dict:
        """Get ranking statistics"""
        try:
            with self._rankings_lock:
                total_queries = sum(self._query_counts.values())
                unique_queries = len(self._query_counts)
                
                return {
                    "total_queries": total_queries,
                    "unique_queries": unique_queries,
                    "top_query": max(self._query_counts.items(), key=lambda x: x[1]) if self._query_counts else None
                }
                
        except Exception as e:
            print(f"Failed to get ranking stats: {e}")
            return {
                "total_queries": 0,
                "unique_queries": 0,
                "top_query": None
            }
    
    def get_user_stats(self) -> Dict:
        """Get statistics about users and searches"""
        stats = {
            "total_searches": 0,
            "unique_users": set(),
            "unique_queries": set()
        }
        
        try:
            # Get all user log files
            user_files = glob.glob(os.path.join(self.log_dir, "*.jsonl"))
            
            for user_file in user_files:
                username = os.path.basename(user_file).replace('.jsonl', '')
                stats["unique_users"].add(username)
                
                with open(user_file, 'r', encoding='utf-8') as f:
                    for line in f:
                        try:
                            entry = json.loads(line.strip())
                            stats["total_searches"] += 1
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