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
import json
import glob


def read_tokenized_batches(tokenized_dir: str) -> List[List[Dict]]:
    """Read pre-tokenized JSON files from directory"""
    print(f"📖 Reading tokenized files from: {tokenized_dir}")
    
    if not os.path.exists(tokenized_dir):
        print(f"❌ Error: Tokenized directory does not exist: {tokenized_dir}")
        return []
    
    # Find all tokenized batch files
    batch_files = glob.glob(os.path.join(tokenized_dir, "tokenized_batch_*.json"))
    batch_files.sort()  # Ensure consistent order
    
    if not batch_files:
        print(f"❌ Error: No tokenized batch files found in {tokenized_dir}")
        print("Expected files like: tokenized_batch_0001.json")
        return []
    
    batches = []
    total_records = 0
    
    try:
        # Read summary if available for validation
        summary_file = os.path.join(tokenized_dir, "tokenization_summary.json")
        if os.path.exists(summary_file):
            with open(summary_file, 'r', encoding='utf-8') as f:
                summary = json.load(f)
                print(f"📋 Found tokenization summary:")
                print(f"   📊 Expected records: {summary['processing_info']['total_records']}")
                print(f"   📦 Expected batches: {summary['processing_info']['total_batches']}")
                print(f"   🔧 Tokenizer: {summary['tokenization_settings']['tokenizer']}")
        
        for batch_file in batch_files:
            with open(batch_file, 'r', encoding='utf-8') as f:
                batch_data = json.load(f)
                
                if not isinstance(batch_data, list):
                    print(f"⚠️  Warning: {batch_file} does not contain a list")
                    continue
                
                # Validate that records have required fields
                if batch_data:
                    required_fields = ['id', 'content_tokens']
                    first_record = batch_data[0]
                    missing_fields = [field for field in required_fields if field not in first_record]
                    if missing_fields:
                        print(f"⚠️  Warning: {batch_file} missing fields: {missing_fields}")
                        continue
                
                batches.append(batch_data)
                total_records += len(batch_data)
        
        print(f"✅ Successfully loaded {total_records} tokenized records from {len(batches)} batch files")
        return batches
        
    except Exception as e:
        print(f"❌ Error reading tokenized files: {e}")
        return []


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


def convert_to_int(value, default: int = 0) -> int:
    """Safely convert string or int to integer"""
    try:
        if isinstance(value, int):
            return value
        if isinstance(value, str):
            return int(value) if value and value.strip() else default
        return default
    except (ValueError, TypeError):
        return default


def process_batch(search_service: SearchService, batch: List[Dict], batch_num: int, is_tokenized: bool = False) -> bool:
    """Process a single batch of documents"""
    print(f"📝 Processing batch {batch_num} ({len(batch)} records)...")
    
    documents = []
    for row in batch:
        # Convert row to document format expected by search service
        doc = {
            'id': row.get('id', ''),
            'url': row.get('url', ''),
            
            # Enterprise corporate identification
            'jcn': row.get('jcn', ''),
            'CUST_STATUS2': row.get('CUST_STATUS2', ''),
            'company_name_kj': row.get('company_name_kj', ''),
            
            # Address information
            'company_address_all': row.get('company_address_all', ''),
            'prefecture': row.get('prefecture', '').lower(),
            'city': row.get('city', ''),
            
            # Industry classification
            'LARGE_CLASS_NAME': row.get('LARGE_CLASS_NAME', ''),
            'MIDDLE_CLASS_NAME': row.get('MIDDLE_CLASS_NAME', ''),
            
            # Financial data (convert to int)
            'CURR_SETLMNT_TAKING_AMT': convert_to_int(row.get('CURR_SETLMNT_TAKING_AMT', '0')),
            'EMPLOYEE_ALL_NUM': convert_to_int(row.get('EMPLOYEE_ALL_NUM', '0')),
            
            # Organization codes
            'district_finalized_cd': row.get('district_finalized_cd', ''),
            'branch_name_cd': row.get('branch_name_cd', ''),
            
            # Website information
            'main_domain_url': row.get('main_domain_url', ''),
            'url_name': row.get('url_name', '')
        }
        
        # Handle content differently based on whether it's pre-tokenized
        if is_tokenized:
            # Use pre-tokenized content tokens directly
            doc['content_tokens'] = row.get('content_tokens', '')
            doc['content'] = row.get('content', '')  # Keep original for display if available
        else:
            # Use original content (will be tokenized by search service)
            doc['content'] = row.get('content', '')
        
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


def get_index_dir(csv_file: str = None, tokenized_dir: str = None, index_dir: str = None) -> str:
    """Generate index directory based on input source"""
    if index_dir:
        # User specified explicit index directory
        return index_dir
    
    if tokenized_dir:
        # Extract base folder from tokenized path
        # data/xxx/tokenized -> data/xxx/index
        base_path = os.path.dirname(tokenized_dir.rstrip('/'))
        return os.path.join(base_path, 'index')
    
    elif csv_file:
        # Auto-generate from CSV filename
        csv_name = os.path.splitext(os.path.basename(csv_file))[0]
        return f"data/{csv_name}/index"
    
    else:
        # Fallback
        return "data/whoosh_index"


def main():
    parser = argparse.ArgumentParser(
        description='Create Whoosh search index from CSV file',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From CSV file (with tokenization)
  python scripts/create_index.py data/companies.csv
  python scripts/create_index.py data/large_dataset.csv --batch-size 1000
  python scripts/create_index.py data/test.csv --batch-size 100 --index-dir data/test_index
  
  # From pre-tokenized files (faster, allows preprocessing)
  python scripts/create_index.py --tokenized-dir data/tokenized/
  python scripts/create_index.py --tokenized-dir data/tokenized/ --index-dir data/custom_index
        """
    )
    
    # Input source - either CSV file or tokenized directory
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('csv_file', nargs='?', help='Path to CSV file containing enterprise data')
    input_group.add_argument('--tokenized-dir', type=str, 
                           help='Directory containing tokenized JSON files from tokenize_csv.py')
    
    parser.add_argument('--batch-size', type=int, default=500, 
                       help='Number of records to process per batch (for CSV input only, default: 500)')
    parser.add_argument('--index-dir', type=str,
                       help='Directory for the search index. If not specified, auto-generates based on input source')
    parser.add_argument('--clear-existing', action='store_true',
                       help='Clear existing index before creating new one')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.csv_file and not os.path.exists(args.csv_file):
        print(f"❌ Error: CSV file does not exist: {args.csv_file}")
        sys.exit(1)
    
    if args.tokenized_dir and not os.path.exists(args.tokenized_dir):
        print(f"❌ Error: Tokenized directory does not exist: {args.tokenized_dir}")
        sys.exit(1)
    
    if args.csv_file and args.batch_size <= 0:
        print("❌ Error: Batch size must be a positive integer")
        sys.exit(1)
    
    # Determine index directory
    index_dir = get_index_dir(args.csv_file, args.tokenized_dir, args.index_dir)
    
    print("🚀 EOS Index Creation Script")
    print("=" * 50)
    if args.csv_file:
        print(f"📂 Input: CSV File - {args.csv_file}")
        print(f"📦 Batch Size: {args.batch_size}")
    else:
        print(f"📂 Input: Tokenized Directory - {args.tokenized_dir}")
        print(f"📦 Batch Size: Determined by tokenized files")
    print(f"🗂️  Index Directory: {index_dir}")
    print()
    
    # Initialize search service
    try:
        search_service = SearchService(index_dir)
        
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
    
    # Read input data
    start_time = time.time()
    if args.csv_file:
        print("🔄 Reading and tokenizing CSV file...")
        batches = read_csv_batch(args.csv_file, args.batch_size)
        input_type = "CSV"
    else:
        print("🔄 Reading pre-tokenized files...")
        batches = read_tokenized_batches(args.tokenized_dir)
        input_type = "Tokenized"
    
    if not batches:
        print(f"❌ No {input_type.lower()} data to process. Exiting.")
        sys.exit(1)
    
    # Process each batch
    successful_batches = 0
    total_records = sum(len(batch) for batch in batches)
    
    print(f"\n🔄 Starting batch processing...")
    print(f"📊 Total records: {total_records}")
    print(f"📦 Total batches: {len(batches)}")
    print()
    
    is_tokenized = (input_type == "Tokenized")
    for i, batch in enumerate(batches, 1):
        if process_batch(search_service, batch, i, is_tokenized):
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
        print(f"💾 Index saved to: {index_dir}")
    else:
        failed_batches = len(batches) - successful_batches
        print(f"⚠️  Index creation completed with {failed_batches} failed batches")
    
    # Performance metrics
    if total_records > 0:
        records_per_second = total_records / elapsed_total
        print(f"⚡ Processing rate: {records_per_second:.1f} records/second")


if __name__ == '__main__':
    main()