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

        # In-memory ranking tracker for both queries and keywords
        self._query_counts = defaultdict(int)
        self._keyword_counts = defaultdict(int)
        self._user_search_counts = {}  # User rankings cache
        self._user_history_cache = defaultdict(list)  # User search history cache
        self._rankings_lock = threading.RLock()

        # Initialize rankings and history from existing logs on startup
        self._initialize_rankings()
    
    def _ensure_log_directory(self):
        """Create log directory if it doesn't exist"""
        os.makedirs(self.log_dir, exist_ok=True)
    
    def _get_user_log_file(self, username: str) -> str:
        """Get the log file path for a specific user"""
        # Sanitize username for safe filename
        safe_username = "".join(c for c in username if c.isalnum() or c in "_-.")
        return os.path.join(self.log_dir, f"{safe_username}.jsonl")
    
    def _extract_keywords(self, query: str) -> List[str]:
        """Extract individual keywords from a query using Japanese tokenization"""
        try:
            # Use the same tokenization as the search engine
            keywords = []
            tokens = self.query_processor.tokenize_japanese(query)
            
            for token in tokens:
                # Filter out very short tokens and common particles
                if len(token) >= 2 and token not in ['の', 'を', 'は', 'が', 'に', 'で', 'と', 'から', 'まで', 'より']:
                    keywords.append(token.lower())
            
            return keywords
        except Exception as e:
            print(f"Error extracting keywords from '{query}': {e}")
            # Fallback to simple space splitting
            return [word.strip().lower() for word in query.split() if len(word.strip()) >= 2]
    
    def _initialize_rankings(self):
        """Initialize in-memory rankings and history from existing log files on startup"""
        print("Initializing search rankings and history from existing logs...")

        try:
            user_files = glob.glob(os.path.join(self.log_dir, "*.jsonl"))
            total_queries_loaded = 0
            total_keywords_loaded = 0
            user_search_counts = defaultdict(int)
            user_history = defaultdict(list)

            with self._rankings_lock:
                for user_file in user_files:
                    username = os.path.basename(user_file).replace('.jsonl', '')
                    user_entries = []

                    with open(user_file, 'r', encoding='utf-8') as f:
                        for line in f:
                            try:
                                entry = json.loads(line.strip())
                                query = entry.get('query', '')
                                # Normalize query for consistent ranking
                                normalized_query = self.query_processor.normalize_query(query).lower()
                                if normalized_query:
                                    # Track full query
                                    self._query_counts[normalized_query] += 1
                                    total_queries_loaded += 1

                                    # Track user search count
                                    user_search_counts[username] += 1

                                    # Store user history entry
                                    user_entries.append(entry)

                                    # Extract and track individual keywords
                                    keywords = self._extract_keywords(normalized_query)
                                    for keyword in keywords:
                                        if keyword:
                                            self._keyword_counts[keyword] += 1
                                            total_keywords_loaded += 1
                            except json.JSONDecodeError:
                                continue

                    # Store user history (most recent first)
                    user_history[username] = sorted(user_entries, key=lambda x: x.get('timestamp', ''), reverse=True)

                # Cache user rankings and history
                self._user_search_counts = dict(user_search_counts)
                self._user_history_cache = dict(user_history)

            print(f"Loaded {total_queries_loaded} queries and {total_keywords_loaded} keywords into rankings")
            print(f"Unique queries: {len(self._query_counts)}, Unique keywords: {len(self._keyword_counts)}")
            print(f"Loaded {len(self._user_search_counts)} users with {sum(len(h) for h in user_history.values())} history entries")

        except Exception as e:
            print(f"Error initializing rankings: {e}")
            # Continue with empty rankings
            self._query_counts = defaultdict(int)
            self._keyword_counts = defaultdict(int)
            self._user_search_counts = {}
            self._user_history_cache = defaultdict(list)
    
    def log_search(self, username: str, query: str, results_count: int = 0,
                   search_time: float = 0.0, prefecture: str = "", cust_status: str = "", city: str = ""):
        """Log a search query by user with detailed information"""
        # Normalize query for consistent tracking
        normalized_query = self.query_processor.normalize_query(query)

        log_entry = {
            "timestamp": datetime.datetime.now().isoformat(),
            "query": normalized_query,
            "results_count": results_count,
            "search_time": round(search_time, 3)
        }

        # Only include prefecture if it's specified
        if prefecture:
            log_entry["prefecture"] = prefecture

        # Only include cust_status if it's specified
        if cust_status:
            log_entry["cust_status"] = cust_status

        # Only include city if it's specified
        if city:
            log_entry["city"] = city

        try:
            # Write to file
            user_log_file = self._get_user_log_file(username)
            with open(user_log_file, 'a', encoding='utf-8') as f:
                f.write(json.dumps(log_entry, ensure_ascii=False) + '\n')

            # Update in-memory rankings and history in real-time
            query_key = normalized_query.strip().lower()
            if query_key:
                with self._rankings_lock:
                    # Track full query
                    self._query_counts[query_key] += 1

                    # Track user search count
                    self._user_search_counts[username] = self._user_search_counts.get(username, 0) + 1

                    # Add to user history cache (prepend to keep most recent first)
                    if username not in self._user_history_cache:
                        self._user_history_cache[username] = []
                    self._user_history_cache[username].insert(0, log_entry)

                    # Extract and track individual keywords
                    keywords = self._extract_keywords(query_key)
                    for keyword in keywords:
                        if keyword:
                            self._keyword_counts[keyword] += 1

        except Exception as e:
            print(f"Failed to log search for {username}: {e}")
    
    def get_user_searches(self, username: str, limit: int = 10) -> List[Dict]:
        """Get search history for a specific user from memory cache (loaded on startup)"""
        try:
            with self._rankings_lock:
                user_history = self._user_history_cache.get(username, [])
                # Return limited entries (already sorted by timestamp desc)
                return user_history[:limit]
        except Exception as e:
            print(f"Failed to get user searches for {username}: {e}")
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
    
    def get_popular_keywords(self, limit: int = 10) -> List[Dict]:
        """Get most popular individual keywords across all users (real-time from memory)"""
        try:
            with self._rankings_lock:
                # Sort by count and return top keywords
                popular = sorted(self._keyword_counts.items(), key=lambda x: x[1], reverse=True)
                return [{"keyword": keyword, "count": count} for keyword, count in popular[:limit]]
                
        except Exception as e:
            print(f"Failed to get popular keywords: {e}")
            return []
    
    def get_rankings_stats(self) -> Dict:
        """Get ranking statistics for both queries and keywords"""
        try:
            with self._rankings_lock:
                total_queries = sum(self._query_counts.values())
                unique_queries = len(self._query_counts)
                total_keywords = sum(self._keyword_counts.values())
                unique_keywords = len(self._keyword_counts)
                
                return {
                    "total_queries": total_queries,
                    "unique_queries": unique_queries,
                    "top_query": max(self._query_counts.items(), key=lambda x: x[1]) if self._query_counts else None,
                    "total_keywords": total_keywords,
                    "unique_keywords": unique_keywords,
                    "top_keyword": max(self._keyword_counts.items(), key=lambda x: x[1]) if self._keyword_counts else None
                }
                
        except Exception as e:
            print(f"Failed to get ranking stats: {e}")
            return {
                "total_queries": 0,
                "unique_queries": 0,
                "top_query": None,
                "total_keywords": 0,
                "unique_keywords": 0,
                "top_keyword": None
            }
    
    def get_user_rankings(self, limit: int = 10) -> List[Dict]:
        """Get user rankings by search count (from memory cache, loaded on startup)"""
        try:
            with self._rankings_lock:
                # Sort by search count and return top users
                sorted_users = sorted(self._user_search_counts.items(), key=lambda x: x[1], reverse=True)

                # Add rank to each user
                rankings = []
                for rank, (username, search_count) in enumerate(sorted_users[:limit], start=1):
                    rankings.append({
                        "username": username,
                        "search_count": search_count,
                        "rank": rank
                    })

                return rankings

        except Exception as e:
            print(f"Failed to get user rankings: {e}")
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