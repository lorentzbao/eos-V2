#!/usr/bin/env python3
"""
Index Deletion Script for EOS Search Engine

Deletes an existing Whoosh search index completely.
Use with caution - this operation is irreversible!

Usage:
    python scripts/delete_index.py [--index-dir INDEX_DIR] [--force]

Example:
    python scripts/delete_index.py
    python scripts/delete_index.py --index-dir data/custom_index --force
"""

import argparse
import os
import sys
import shutil

# Add the parent directory to the path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.search_service_prefecture import SearchServicePrefecture


def confirm_deletion(index_dir: str, force: bool = False) -> bool:
    """Ask user for confirmation before deleting index"""
    if force:
        return True
    
    print(f"⚠️  WARNING: This will permanently delete the search index at:")
    print(f"📂 {os.path.abspath(index_dir)}")
    print()
    print("This operation cannot be undone!")
    print()
    
    while True:
        response = input("Are you sure you want to delete this index? (yes/no): ").strip().lower()
        if response in ['yes', 'y']:
            return True
        elif response in ['no', 'n']:
            return False
        else:
            print("Please enter 'yes' or 'no'")


def get_index_info(search_service: SearchService) -> dict:
    """Get information about the current index"""
    try:
        stats = search_service.get_stats()
        return {
            'exists': True,
            'total_documents': stats.get('total_documents', 0),
            'engine_type': stats.get('engine_type', 'Unknown'),
            'cache_size': stats.get('cache_size', 0)
        }
    except Exception as e:
        return {
            'exists': False,
            'error': str(e)
        }


def delete_index_directory(index_dir: str) -> bool:
    """Delete the entire index directory"""
    try:
        if os.path.exists(index_dir):
            shutil.rmtree(index_dir)
            print(f"🗑️  Successfully deleted directory: {index_dir}")
            return True
        else:
            print(f"ℹ️  Directory does not exist: {index_dir}")
            return True
    except Exception as e:
        print(f"❌ Error deleting directory: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Delete Whoosh search index',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/delete_index.py
  python scripts/delete_index.py --index-dir data/custom_index
  python scripts/delete_index.py --force  # Skip confirmation prompt

⚠️  WARNING: This operation is irreversible!
        """
    )
    
    parser.add_argument('--index-dir', type=str, default='data/whoosh_index',
                       help='Directory containing the search index to delete (default: data/whoosh_index)')
    parser.add_argument('--force', action='store_true',
                       help='Skip confirmation prompt and delete immediately')
    parser.add_argument('--stats-only', action='store_true',
                       help='Show index statistics without deleting')
    
    args = parser.parse_args()
    
    print("🗑️  EOS Index Deletion Script")
    print("=" * 50)
    print(f"📂 Index Directory: {args.index_dir}")
    print()
    
    # Check if index directory exists
    if not os.path.exists(args.index_dir):
        print(f"ℹ️  Index directory does not exist: {args.index_dir}")
        print("✅ Nothing to delete.")
        sys.exit(0)
    
    # Initialize search service to get index information
    try:
        search_service = SearchServicePrefecture(args.index_dir)
        index_info = get_index_info(search_service)
        
        print("📊 INDEX INFORMATION")
        print("-" * 30)
        if index_info['exists']:
            print(f"📄 Total Documents: {index_info['total_documents']}")
            print(f"🔍 Engine Type: {index_info['engine_type']}")
            print(f"💾 Cache Size: {index_info['cache_size']}")
        else:
            print(f"❌ Index appears to be corrupted or invalid")
            print(f"Error: {index_info.get('error', 'Unknown error')}")
        
        print()
        
    except Exception as e:
        print(f"⚠️  Warning: Could not read index information: {e}")
        print("Index directory exists but may be corrupted.")
        print()
    
    # Show directory size information
    try:
        total_size = 0
        file_count = 0
        for dirpath, dirnames, filenames in os.walk(args.index_dir):
            for filename in filenames:
                filepath = os.path.join(dirpath, filename)
                total_size += os.path.getsize(filepath)
                file_count += 1
        
        size_mb = total_size / (1024 * 1024)
        print(f"📁 Directory Size: {size_mb:.2f} MB ({file_count} files)")
        print()
        
    except Exception as e:
        print(f"⚠️  Could not calculate directory size: {e}")
        print()
    
    # If stats-only mode, exit here
    if args.stats_only:
        print("ℹ️  Stats-only mode. Index not deleted.")
        sys.exit(0)
    
    # Confirm deletion
    if not confirm_deletion(args.index_dir, args.force):
        print("❌ Index deletion cancelled by user.")
        sys.exit(0)
    
    print()
    print("🗑️  Deleting index...")
    
    # Delete using search service first (cleaner approach)
    try:
        if 'search_service' in locals():
            print("🧹 Clearing index using search service...")
            search_service.clear_index()
            print("✅ Index cleared successfully")
    except Exception as e:
        print(f"⚠️  Warning: Could not clear index cleanly: {e}")
        print("Proceeding with directory deletion...")
    
    # Delete the entire directory
    if delete_index_directory(args.index_dir):
        print()
        print("🎉 Index deletion completed successfully!")
        print(f"📂 Deleted: {args.index_dir}")
        
        # Verify deletion
        if not os.path.exists(args.index_dir):
            print("✅ Verification: Index directory no longer exists")
        else:
            print("⚠️  Warning: Index directory still exists (some files may remain)")
    else:
        print()
        print("❌ Index deletion failed!")
        print("Some files may still exist. Check the directory manually.")
        sys.exit(1)


if __name__ == '__main__':
    main()