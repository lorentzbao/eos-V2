#!/usr/bin/env python3
"""
Index Creation Script for EOS Search Engine

Creates a new Whoosh search index from a CSV file with enterprise data.
Supports batch processing for large datasets.

Usage:
    python scripts/create_index.py <csv_file> [--batch-size BATCH_SIZE] [--index-dir INDEX_DIR]

Example:
    python scripts/create_index.py data/enterprise_data.csv --batch-size 1000
    python scripts/create_index.py data/companies.csv --batch-size 500 --index-dir data/custom_index
"""

import argparse
import csv
import os
import sys
import time
from typing import List, Dict

# Add the parent directory to the path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.search_service import SearchService


def read_csv_batch(csv_file: str, batch_size: int) -> List[List[Dict]]:
    """Read CSV file and yield batches of records"""
    batches = []
    current_batch = []
    
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
                return []
            
            total_rows = 0
            for row in reader:
                # Skip empty rows
                if not row.get('id') or not row.get('content'):
                    continue
                    
                current_batch.append(row)
                total_rows += 1
                
                if len(current_batch) >= batch_size:
                    batches.append(current_batch)
                    current_batch = []
            
            # Add remaining records
            if current_batch:
                batches.append(current_batch)
            
            print(f"✅ Successfully read {total_rows} records in {len(batches)} batches")
            return batches
            
    except FileNotFoundError:
        print(f"❌ Error: CSV file not found: {csv_file}")
        return []
    except Exception as e:
        print(f"❌ Error reading CSV file: {e}")
        return []


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
        description='Create Whoosh search index from CSV file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/create_index.py data/companies.csv
  python scripts/create_index.py data/large_dataset.csv --batch-size 1000
  python scripts/create_index.py data/test.csv --batch-size 100 --index-dir data/test_index
        """
    )
    
    parser.add_argument('csv_file', help='Path to CSV file containing enterprise data')
    parser.add_argument('--batch-size', type=int, default=500, 
                       help='Number of records to process per batch (default: 500)')
    parser.add_argument('--index-dir', type=str, default='data/whoosh_index',
                       help='Directory for the search index (default: data/whoosh_index)')
    parser.add_argument('--clear-existing', action='store_true',
                       help='Clear existing index before creating new one')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not os.path.exists(args.csv_file):
        print(f"❌ Error: CSV file does not exist: {args.csv_file}")
        sys.exit(1)
    
    if args.batch_size <= 0:
        print("❌ Error: Batch size must be a positive integer")
        sys.exit(1)
    
    print("🚀 EOS Index Creation Script")
    print("=" * 50)
    print(f"📂 CSV File: {args.csv_file}")
    print(f"📦 Batch Size: {args.batch_size}")
    print(f"🗂️  Index Directory: {args.index_dir}")
    print()
    
    # Initialize search service
    try:
        search_service = SearchService(args.index_dir)
        
        # Clear existing index if requested
        if args.clear_existing:
            print("🗑️  Clearing existing index...")
            search_service.clear_index()
            print("✅ Existing index cleared")
        
        # Get initial document count
        initial_count = search_service.get_stats()['total_documents']
        print(f"📊 Initial document count: {initial_count}")
        
    except Exception as e:
        print(f"❌ Error initializing search service: {e}")
        sys.exit(1)
    
    # Read CSV file in batches
    start_time = time.time()
    batches = read_csv_batch(args.csv_file, args.batch_size)
    
    if not batches:
        print("❌ No data to process. Exiting.")
        sys.exit(1)
    
    # Process each batch
    successful_batches = 0
    total_records = sum(len(batch) for batch in batches)
    
    print(f"\n🔄 Starting batch processing...")
    print(f"📊 Total records: {total_records}")
    print(f"📦 Total batches: {len(batches)}")
    print()
    
    for i, batch in enumerate(batches, 1):
        if process_batch(search_service, batch, i):
            successful_batches += 1
        
        # Show progress
        progress = (i / len(batches)) * 100
        print(f"📈 Progress: {progress:.1f}% ({i}/{len(batches)} batches)")
        print()
    
    # Final statistics
    elapsed_total = time.time() - start_time
    final_count = search_service.get_stats()['total_documents']
    added_count = final_count - initial_count
    
    print("=" * 50)
    print("📊 FINAL STATISTICS")
    print("=" * 50)
    print(f"⏱️  Total time: {elapsed_total:.2f} seconds")
    print(f"✅ Successful batches: {successful_batches}/{len(batches)}")
    print(f"📝 Records processed: {total_records}")
    print(f"📄 Documents added to index: {added_count}")
    print(f"🗂️  Final index size: {final_count} documents")
    
    if successful_batches == len(batches):
        print("🎉 Index creation completed successfully!")
        print(f"💾 Index saved to: {args.index_dir}")
    else:
        failed_batches = len(batches) - successful_batches
        print(f"⚠️  Index creation completed with {failed_batches} failed batches")
    
    # Performance metrics
    if total_records > 0:
        records_per_second = total_records / elapsed_total
        print(f"⚡ Processing rate: {records_per_second:.1f} records/second")


if __name__ == '__main__':
    main()