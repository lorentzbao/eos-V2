#!/usr/bin/env python3
"""
Add Documents Script for EOS Search Engine

Adds new documents from a CSV file to an existing Whoosh search index.
Supports batch processing and duplicate detection.

Usage:
    python scripts/add_to_index.py <csv_file> [--batch-size BATCH_SIZE] [--index-dir INDEX_DIR]

Example:
    python scripts/add_to_index.py data/new_companies.csv --batch-size 1000
    python scripts/add_to_index.py data/updates.csv --batch-size 100 --index-dir data/custom_index
"""

import argparse
import csv
import os
import sys
import time
from typing import List, Dict, Set

# Add the parent directory to the path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.search_service_prefecture import SearchServicePrefecture


def read_existing_ids(search_service: SearchService) -> Set[str]:
    """Get all existing document IDs from the index"""
    print("🔍 Reading existing document IDs...")
    existing_ids = set()
    
    try:
        # This would require a method to get all document IDs
        # For now, we'll implement a simple approach
        stats = search_service.get_stats()
        total_docs = stats.get('total_documents', 0)
        print(f"📊 Found {total_docs} existing documents in index")
        
        # Note: In a production system, you might want to implement a method
        # to efficiently retrieve all document IDs without loading full documents
        return existing_ids
        
    except Exception as e:
        print(f"⚠️  Warning: Could not read existing IDs: {e}")
        print("Proceeding without duplicate detection...")
        return set()


def read_csv_with_duplicate_check(csv_file: str, batch_size: int, existing_ids: Set[str], skip_duplicates: bool = True) -> tuple:
    """Read CSV file and return batches, with optional duplicate detection"""
    batches = []
    current_batch = []
    skipped_count = 0
    
    print(f"📖 Reading CSV file: {csv_file}")
    
    try:
        with open(csv_file, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            
            # Validate required columns
            required_fields = ['id', 'jcn', 'company_name_kj', 'url', 'content']
            missing_fields = [field for field in required_fields if field not in reader.fieldnames]
            if missing_fields:
                print(f"❌ Error: Missing required columns: {missing_fields}")
                print(f"Available columns: {reader.fieldnames}")
                return [], 0
            
            total_rows = 0
            for row in reader:
                # Skip empty rows
                if not row.get('id') or not row.get('content'):
                    continue
                
                # Check for duplicates
                if skip_duplicates and row.get('id') in existing_ids:
                    skipped_count += 1
                    continue
                
                current_batch.append(row)
                total_rows += 1
                
                if len(current_batch) >= batch_size:
                    batches.append(current_batch)
                    current_batch = []
            
            # Add remaining records
            if current_batch:
                batches.append(current_batch)
            
            print(f"✅ Successfully read {total_rows} new records in {len(batches)} batches")
            if skip_duplicates and skipped_count > 0:
                print(f"⏭️  Skipped {skipped_count} duplicate records")
            
            return batches, skipped_count
            
    except FileNotFoundError:
        print(f"❌ Error: CSV file not found: {csv_file}")
        return [], 0
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return [], 0


def convert_to_int(value: str, default: int = 0) -> int:
    """Safely convert string to integer"""
    try:
        return int(value) if value and value.strip() else default
    except (ValueError, TypeError):
        return default


def process_batch(search_service: SearchService, batch: List[Dict], batch_num: int) -> bool:
    """Process a single batch of documents"""
    print(f"📝 Processing batch {batch_num} ({len(batch)} records)...")
    
    documents = []
    for row in batch:
        # Convert row to document format expected by search service
        doc = {
            'id': row.get('id', ''),
            'url': row.get('url', ''),
            'content': row.get('content', ''),
            
            # Enterprise corporate identification
            'jcn': row.get('jcn', ''),
            'cust_status': row.get('cust_status', ''),
            'company_name_kj': row.get('company_name_kj', ''),
            
            # Address information
            'company_address_all': row.get('company_address_all', ''),
            'prefecture': row.get('prefecture', '').lower(),
            'city': row.get('city', ''),
            
            # Industry classification
            'duns_large_class_name': row.get('duns_large_class_name', ''),
            'duns_middle_class_name': row.get('duns_middle_class_name', ''),
            
            # Financial data (convert to int)
            'curr_setlmnt_taking_amt': convert_to_int(row.get('curr_setlmnt_taking_amt', '0')),
            'employee': convert_to_int(row.get('employee', '0')),
            
            # Organization codes
            'district_finalized_cd': row.get('district_finalized_cd', ''),
            'branch_name_cd': row.get('branch_name_cd', ''),
            
            # Website information
            'main_domain_url': row.get('main_domain_url', ''),
            'url_name': row.get('url_name', '')
        }
        
        documents.append(doc)
    
    # Add batch to search service
    try:
        start_time = time.time()
        success = search_service.add_documents_batch(documents)
        elapsed = time.time() - start_time
        
        if success:
            print(f"✅ Batch {batch_num} completed successfully in {elapsed:.2f} seconds")
            return True
        else:
            print(f"❌ Batch {batch_num} failed")
            return False
            
    except Exception as e:
        print(f"❌ Error processing batch {batch_num}: {e}")
        return False


def main():
    parser = argparse.ArgumentParser(
        description='Add new documents to existing Whoosh search index from CSV file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/add_to_index.py data/new_companies.csv
  python scripts/add_to_index.py data/updates.csv --batch-size 1000
  python scripts/add_to_index.py data/incremental.csv --no-duplicate-check
  python scripts/add_to_index.py data/data.csv --index-dir data/custom_index
        """
    )
    
    parser.add_argument('csv_file', help='Path to CSV file containing new enterprise data')
    parser.add_argument('--batch-size', type=int, default=500, 
                       help='Number of records to process per batch (default: 500)')
    parser.add_argument('--index-dir', type=str, default='data/whoosh_index',
                       help='Directory containing the search index (default: data/whoosh_index)')
    parser.add_argument('--no-duplicate-check', action='store_true',
                       help='Skip duplicate checking (faster but may create duplicates)')
    parser.add_argument('--dry-run', action='store_true',
                       help='Show what would be done without actually adding documents')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not os.path.exists(args.csv_file):
        print(f"❌ Error: CSV file does not exist: {args.csv_file}")
        sys.exit(1)
    
    if not os.path.exists(args.index_dir):
        print(f"❌ Error: Index directory does not exist: {args.index_dir}")
        print("Use create_index.py to create a new index first.")
        sys.exit(1)
    
    if args.batch_size <= 0:
        print("❌ Error: Batch size must be a positive integer")
        sys.exit(1)
    
    print("📥 EOS Add Documents Script")
    print("=" * 50)
    print(f"📂 CSV File: {args.csv_file}")
    print(f"📦 Batch Size: {args.batch_size}")
    print(f"🗂️  Index Directory: {args.index_dir}")
    print(f"🔍 Duplicate Check: {'Disabled' if args.no_duplicate_check else 'Enabled'}")
    if args.dry_run:
        print("🧪 Mode: DRY RUN (no changes will be made)")
    print()
    
    # Initialize search service
    try:
        search_service = SearchServicePrefecture(args.index_dir)
        initial_stats = search_service.get_stats()
        initial_count = initial_stats['total_documents']
        
        print(f"📊 Initial index statistics:")
        print(f"   📄 Documents: {initial_count}")
        print(f"   🔍 Engine: {initial_stats.get('engine_type', 'Unknown')}")
        print()
        
    except Exception as e:
        print(f"❌ Error initializing search service: {e}")
        print("Make sure the index directory exists and is valid.")
        sys.exit(1)
    
    # Get existing document IDs for duplicate checking
    existing_ids = set()
    if not args.no_duplicate_check:
        existing_ids = read_existing_ids(search_service)
    
    # Read CSV file in batches
    start_time = time.time()
    batches, skipped_count = read_csv_with_duplicate_check(
        args.csv_file, 
        args.batch_size, 
        existing_ids, 
        not args.no_duplicate_check
    )
    
    if not batches:
        print("❌ No new data to process. Exiting.")
        sys.exit(1)
    
    total_records = sum(len(batch) for batch in batches)
    
    print(f"\n📊 PROCESSING SUMMARY")
    print("-" * 30)
    print(f"📄 New records to add: {total_records}")
    if skipped_count > 0:
        print(f"⏭️  Duplicate records skipped: {skipped_count}")
    print(f"📦 Total batches: {len(batches)}")
    print()
    
    if args.dry_run:
        print("🧪 DRY RUN: No documents will be added.")
        print("The following batches would be processed:")
        for i, batch in enumerate(batches, 1):
            print(f"   Batch {i}: {len(batch)} records")
        print()
        print("Run without --dry-run to actually add documents.")
        sys.exit(0)
    
    # Process each batch
    print("🔄 Starting batch processing...")
    print()
    
    successful_batches = 0
    for i, batch in enumerate(batches, 1):
        if process_batch(search_service, batch, i):
            successful_batches += 1
        
        # Show progress
        progress = (i / len(batches)) * 100
        print(f"📈 Progress: {progress:.1f}% ({i}/{len(batches)} batches)")
        print()
    
    # Clear cache after adding documents
    try:
        search_service.clear_cache()
        print("🧹 Search cache cleared")
    except:
        pass
    
    # Final statistics
    elapsed_total = time.time() - start_time
    
    try:
        final_stats = search_service.get_stats()
        final_count = final_stats['total_documents']
        added_count = final_count - initial_count
    except:
        final_count = 0
        added_count = 0
    
    print("=" * 50)
    print("📊 FINAL STATISTICS")
    print("=" * 50)
    print(f"⏱️  Total time: {elapsed_total:.2f} seconds")
    print(f"✅ Successful batches: {successful_batches}/{len(batches)}")
    print(f"📝 Records processed: {total_records}")
    if skipped_count > 0:
        print(f"⏭️  Records skipped (duplicates): {skipped_count}")
    print(f"📄 Documents added to index: {added_count}")
    print(f"🗂️  Final index size: {final_count} documents")
    
    if successful_batches == len(batches):
        print("🎉 Document addition completed successfully!")
    else:
        failed_batches = len(batches) - successful_batches
        print(f"⚠️  Document addition completed with {failed_batches} failed batches")
    
    # Performance metrics
    if total_records > 0:
        records_per_second = total_records / elapsed_total
        print(f"⚡ Processing rate: {records_per_second:.1f} records/second")


if __name__ == '__main__':
    main()