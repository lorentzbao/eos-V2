import os
import json
import datetime
from typing import List, Dict
import glob

class SearchLogger:
    """Log and track user search queries using per-user log files"""
    
    def __init__(self, log_dir="data/search_logs"):
        self.log_dir = log_dir
        self._ensure_log_directory()
    
    def _ensure_log_directory(self):
        """Create log directory if it doesn't exist"""
        os.makedirs(self.log_dir, exist_ok=True)
    
    def _get_user_log_file(self, username: str) -> str:
        """Get the log file path for a specific user"""
        # Sanitize username for safe filename
        safe_username = "".join(c for c in username if c.isalnum() or c in "_-.")
        return os.path.join(self.log_dir, f"{safe_username}.jsonl")
    
    def log_search(self, username: str, query: str, search_type: str = "auto", 
                   results_count: int = 0, search_time: float = 0.0, prefecture: str = ""):
        """Log a search query by user with detailed information"""
        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "query": query,
            "search_type": search_type,
            "results_count": results_count,
            "search_time": round(search_time, 3)
        }
        
        # Only include prefecture if it's specified
        if prefecture:
            log_entry["prefecture"] = prefecture
        
        try:
            user_log_file = self._get_user_log_file(username)
            with open(user_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')
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
        """Get most popular search queries across all users"""
        query_counts = {}
        
        try:
            # Get all user log files
            user_files = glob.glob(os.path.join(self.log_dir, "*.jsonl"))
            
            for user_file in user_files:
                with open(user_file, 'r', encoding='utf-8') as f:
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