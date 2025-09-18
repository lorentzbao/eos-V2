#!/usr/bin/env python3
"""
Index Information Script for EOS Search Engine

Shows detailed information about an existing Whoosh search index.

Usage:
    python scripts/index_info.py [--index-dir INDEX_DIR]

Example:
    python scripts/index_info.py
    python scripts/index_info.py --index-dir data/custom_index
"""

import argparse
import os
import sys
import time
from datetime import datetime

# Add the parent directory to the path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.search_service import SearchService


def format_bytes(bytes_size: int) -> str:
    """Format bytes to human readable format"""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if bytes_size < 1024:
            return f"{bytes_size:.1f} {unit}"
        bytes_size /= 1024
    return f"{bytes_size:.1f} TB"


def get_directory_info(index_dir: str) -> dict:
    """Get directory size and file information"""
    info = {
        'exists': False,
        'total_size': 0,
        'file_count': 0,
        'files': [],
        'created_time': None,
        'modified_time': None
    }
    
    try:
        if not os.path.exists(index_dir):
            return info
            
        info['exists'] = True
        
        # Get directory timestamps
        stat = os.stat(index_dir)
        info['created_time'] = datetime.fromtimestamp(stat.st_ctime)
        info['modified_time'] = datetime.fromtimestamp(stat.st_mtime)
        
        # Walk through all files
        for dirpath, dirnames, filenames in os.walk(index_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                try:
                    file_stat = os.stat(filepath)
                    file_size = file_stat.st_size
                    file_modified = datetime.fromtimestamp(file_stat.st_mtime)
                    
                    info['total_size'] += file_size
                    info['file_count'] += 1
                    info['files'].append({
                        'name': filename,
                        'size': file_size,
                        'size_formatted': format_bytes(file_size),
                        'modified': file_modified
                    })
                except (OSError, IOError):
                    continue
        
        # Sort files by size (largest first)
        info['files'].sort(key=lambda x: x['size'], reverse=True)
        
    except Exception as e:
        info['error'] = str(e)
    
    return info


def test_search_performance(search_service: SearchService) -> dict:
    """Test basic search performance"""
    test_queries = ['技術', 'サービス', '東京', '開発']
    performance = {
        'tests': [],
        'avg_time': 0,
        'total_results': 0
    }
    
    print("🔍 Testing search performance...")
    
    try:
        total_time = 0
        total_results = 0
        
        for query in test_queries:
            start_time = time.time()
            results = search_service.search(query, limit=10)
            end_time = time.time()
            
            search_time = end_time - start_time
            result_count = results.get('total_found', 0)
            
            performance['tests'].append({
                'query': query,
                'time': search_time,
                'results': result_count
            })
            
            total_time += search_time
            total_results += result_count
            
            print(f"   📝 '{query}': {result_count} results in {search_time:.3f}s")
        
        performance['avg_time'] = total_time / len(test_queries)
        performance['total_results'] = total_results
        
    except Exception as e:
        performance['error'] = str(e)
    
    return performance


def main():
    parser = argparse.ArgumentParser(
        description='Show detailed information about Whoosh search index',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/index_info.py
  python scripts/index_info.py --index-dir data/custom_index
  python scripts/index_info.py --no-performance-test
        """
    )
    
    parser.add_argument('--index-dir', type=str, default='data/whoosh_index',
                       help='Directory containing the search index (default: data/whoosh_index)')
    parser.add_argument('--no-performance-test', action='store_true',
                       help='Skip search performance testing')
    parser.add_argument('--detailed-files', action='store_true',
                       help='Show detailed file listing')
    
    args = parser.parse_args()
    
    print("📊 EOS Index Information")
    print("=" * 60)
    print(f"📂 Index Directory: {args.index_dir}")
    print(f"📍 Full Path: {os.path.abspath(args.index_dir)}")
    print()
    
    # Check directory information
    dir_info = get_directory_info(args.index_dir)
    
    if not dir_info['exists']:
        print("❌ Index directory does not exist!")
        print()
        print("Use create_index.py to create a new index:")
        print(f"python scripts/create_index.py data/sample.csv --index-dir {args.index_dir}")
        sys.exit(1)
    
    # Directory statistics
    print("📁 DIRECTORY INFORMATION")
    print("-" * 40)
    print(f"📦 Total Size: {format_bytes(dir_info['total_size'])}")
    print(f"📄 File Count: {dir_info['file_count']}")
    if dir_info.get('created_time'):
        print(f"📅 Created: {dir_info['created_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    if dir_info.get('modified_time'):
        print(f"🔄 Modified: {dir_info['modified_time'].strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # File listing
    if args.detailed_files and dir_info['files']:
        print("📋 FILE LISTING")
        print("-" * 40)
        for file_info in dir_info['files']:
            print(f"   {file_info['name']:<25} {file_info['size_formatted']:>10} {file_info['modified'].strftime('%Y-%m-%d %H:%M')}")
        print()
    
    # Initialize search service and get index information
    try:
        print("🔍 SEARCH ENGINE INFORMATION")
        print("-" * 40)
        
        search_service = SearchService(args.index_dir)
        stats = search_service.get_stats()
        
        print(f"📄 Total Documents: {stats.get('total_documents', 0):,}")
        print(f"🔍 Engine Type: {stats.get('engine_type', 'Unknown')}")
        
        # Cache information
        if 'cache_hits' in stats:
            cache_hit_rate = 0
            if stats.get('cache_hits', 0) + stats.get('cache_misses', 0) > 0:
                cache_hit_rate = (stats.get('cache_hits', 0) / (stats.get('cache_hits', 0) + stats.get('cache_misses', 0))) * 100
            
            print(f"💾 Cache Size: {stats.get('cache_size', 0)}/{stats.get('cache_max_size', 0)}")
            print(f"🎯 Cache Hit Rate: {cache_hit_rate:.1f}%")
            print(f"   📈 Hits: {stats.get('cache_hits', 0):,}")
            print(f"   📉 Misses: {stats.get('cache_misses', 0):,}")
        
        print()
        
        # Performance testing
        if not args.no_performance_test:
            performance = test_search_performance(search_service)
            
            print("⚡ PERFORMANCE TEST RESULTS")
            print("-" * 40)
            
            if 'error' in performance:
                print(f"❌ Performance test failed: {performance['error']}")
            else:
                print(f"⏱️  Average Search Time: {performance['avg_time']:.3f} seconds")
                print(f"📊 Total Results Found: {performance['total_results']:,}")
                print(f"🔍 Queries Tested: {len(performance['tests'])}")
                
                if performance['avg_time'] < 0.1:
                    print("🚀 Performance: Excellent (< 0.1s)")
                elif performance['avg_time'] < 0.5:
                    print("✅ Performance: Good (< 0.5s)")
                elif performance['avg_time'] < 1.0:
                    print("⚠️  Performance: Fair (< 1.0s)")
                else:
                    print("🐌 Performance: Slow (> 1.0s)")
            
            print()
        
        # Health check
        print("🏥 INDEX HEALTH CHECK")
        print("-" * 40)
        
        health_issues = []
        
        # Check for common issues
        if stats.get('total_documents', 0) == 0:
            health_issues.append("No documents in index")
        
        if dir_info['total_size'] == 0:
            health_issues.append("Index directory is empty")
        
        if dir_info['file_count'] < 2:
            health_issues.append("Very few index files (may be incomplete)")
        
        # Check for very old index
        if dir_info.get('modified_time'):
            days_old = (datetime.now() - dir_info['modified_time']).days
            if days_old > 30:
                health_issues.append(f"Index is {days_old} days old (may need refresh)")
        
        if health_issues:
            print("⚠️  Issues found:")
            for issue in health_issues:
                print(f"   • {issue}")
        else:
            print("✅ Index appears healthy")
        
        print()
        
        # Recommendations
        print("💡 RECOMMENDATIONS")
        print("-" * 40)
        
        if stats.get('total_documents', 0) > 100000:
            print("• Consider using larger batch sizes for better performance")
        
        if performance.get('avg_time', 0) > 0.5:
            print("• Search performance could be improved - consider index optimization")
        
        if dir_info['total_size'] > 1024 * 1024 * 1024:  # > 1GB
            print("• Large index size - monitor disk space")
        
        cache_hit_rate = 0
        if stats.get('cache_hits', 0) + stats.get('cache_misses', 0) > 0:
            cache_hit_rate = (stats.get('cache_hits', 0) / (stats.get('cache_hits', 0) + stats.get('cache_misses', 0))) * 100
        
        if cache_hit_rate < 50 and stats.get('cache_hits', 0) + stats.get('cache_misses', 0) > 10:
            print("• Low cache hit rate - consider increasing cache size")
        
        print("• Regular backups recommended for production indexes")
        print("• Monitor search logs for common queries and optimization opportunities")
        
    except Exception as e:
        print(f"❌ Error accessing search index: {e}")
        print()
        print("The index may be corrupted or incompatible.")
        print("Consider recreating the index with create_index.py")
        sys.exit(1)


if __name__ == '__main__':
    main()