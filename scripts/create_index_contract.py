#!/usr/bin/env python3
"""
Contract Index Creation Script for EOS Search Engine

Creates Whoosh search indexes from district-based contract tokenized data.
Each district (A, B, C...) gets its own index.

Usage:
    python scripts/create_index_contract.py [--district DISTRICT] [--batch-size BATCH_SIZE] [--clear-existing]

Example:
    # Create indexes for all districts
    python scripts/create_index_contract.py

    # Create index for specific district
    python scripts/create_index_contract.py --district A

    # Clear and rebuild all indexes
    python scripts/create_index_contract.py --clear-existing
"""

import argparse
import json
import os
import sys
import time
import glob
from typing import List, Dict

# Add the parent directory to the path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.search_service_contract import SearchServiceContract


# District mapping (must match create_contract_tokenized.py)
DISTRICT_MAPPING = {
    "北海道・東北地域事業本部": "A",
    "関信越地域事業本部": "B",
    "首都圏地域事業本部": "C",
    "東海・北陸地域事業本部": "D",
    "関西地域事業本部": "E",
    "中国・四国地域事業本部": "F",
    "九州・沖縄地域事業本部": "G",
    "本店グループ": "H",
    "企業営業本部": "I",
    "全国代理店センター本部": "J",
    "企業営業グループ": "K"
}

# Reverse mapping for display
DISTRICT_NAMES = {v: k for k, v in DISTRICT_MAPPING.items()}


def read_contract_tokenized_batches(district: str, tokenized_base_dir: str = "data/tokenized_contract") -> List[List[Dict]]:
    """Read pre-tokenized contract JSON files for a specific district"""
    district_dir = os.path.join(tokenized_base_dir, district)
    print(f"📖 Reading tokenized files from: {district_dir}")

    if not os.path.exists(district_dir):
        print(f"❌ Error: District directory does not exist: {district_dir}")
        return []

    # Find all batch files
    batch_files = glob.glob(os.path.join(district_dir, "batch_*.json"))
    batch_files.sort()  # Ensure consistent order

    if not batch_files:
        print(f"❌ Error: No batch files found in {district_dir}")
        return []

    batches = []
    total_records = 0

    try:
        for batch_file in batch_files:
            with open(batch_file, 'r', encoding='utf-8') as f:
                batch_data = json.load(f)

                if not isinstance(batch_data, list):
                    print(f"⚠️  Warning: {batch_file} does not contain a list")
                    continue

                # Validate that records have required fields
                if batch_data:
                    required_fields = ['id', 'content_tokens', 'DISTRICT_NAME', 'MOTHERBRANCH_CD', 'SOLICITOR_CD']
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


def process_batch(search_service: SearchServiceContract, batch: List[Dict], batch_num: int) -> bool:
    """Process a single batch of contract documents"""
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
            'url_name': row.get('url_name', ''),

            # Contract-specific fields
            'DISTRICT_NAME': row.get('DISTRICT_NAME', ''),
            'MOTHERBRANCH_CD': row.get('MOTHERBRANCH_CD', ''),
            'BRANCH_NAME': row.get('BRANCH_NAME', ''),
            'SOLICITOR_CD': row.get('SOLICITOR_CD', ''),
            'SOLICITOR': row.get('SOLICITOR', ''),

            # Use pre-tokenized content
            'content_tokens': row.get('content_tokens', ''),
            'content': row.get('content', '')  # Keep original for display if available
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


def process_district(district: str, tokenized_base_dir: str, index_base_dir: str, clear_existing: bool = False):
    """Process a single district"""
    district_name = DISTRICT_NAMES.get(district, f"District {district}")
    index_dir = os.path.join(index_base_dir, district)

    print(f"\n{'='*60}")
    print(f"Processing District {district}: {district_name}")
    print(f"{'='*60}")
    print(f"🗂️  Index Directory: {index_dir}")
    print()

    # Initialize search service
    try:
        search_service = SearchServiceContract(index_dir)

        # Clear existing index if requested
        if clear_existing:
            print("🗑️  Clearing existing index...")
            search_service.clear_index()
            print("✅ Existing index cleared")

        # Get initial document count
        initial_count = search_service.get_stats()['total_documents']
        print(f"📊 Initial document count: {initial_count}")

    except Exception as e:
        print(f"❌ Error initializing search service: {e}")
        return None

    # Read tokenized data
    start_time = time.time()
    batches = read_contract_tokenized_batches(district, tokenized_base_dir)

    if not batches:
        print(f"❌ No tokenized data to process for district {district}. Skipping.")
        return None

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

    print("=" * 60)
    print(f"📊 DISTRICT {district} STATISTICS")
    print("=" * 60)
    print(f"⏱️  Total time: {elapsed_total:.2f} seconds")
    print(f"✅ Successful batches: {successful_batches}/{len(batches)}")
    print(f"📝 Records processed: {total_records}")
    print(f"📄 Documents added to index: {added_count}")
    print(f"🗂️  Final index size: {final_count} documents")

    if successful_batches == len(batches):
        print(f"🎉 District {district} index creation completed successfully!")
    else:
        failed_batches = len(batches) - successful_batches
        print(f"⚠️  District {district} index creation completed with {failed_batches} failed batches")

    # Performance metrics
    if total_records > 0:
        records_per_second = total_records / elapsed_total
        print(f"⚡ Processing rate: {records_per_second:.1f} records/second")

    return {
        'district': district,
        'district_name': district_name,
        'total_records': total_records,
        'added_count': added_count,
        'final_count': final_count,
        'successful_batches': successful_batches,
        'total_batches': len(batches),
        'elapsed_time': elapsed_total
    }


def get_available_districts(tokenized_base_dir: str) -> List[str]:
    """Get list of districts that have tokenized data"""
    if not os.path.exists(tokenized_base_dir):
        return []

    districts = []
    for item in os.listdir(tokenized_base_dir):
        item_path = os.path.join(tokenized_base_dir, item)
        if os.path.isdir(item_path) and item in DISTRICT_NAMES:
            # Check if it has batch files
            batch_files = glob.glob(os.path.join(item_path, "batch_*.json"))
            if batch_files:
                districts.append(item)

    return sorted(districts)


def main():
    parser = argparse.ArgumentParser(
        description='Create Whoosh search indexes from contract tokenized data',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Create indexes for all districts
  python scripts/create_index_contract.py

  # Create index for specific district
  python scripts/create_index_contract.py --district A

  # Clear and rebuild all indexes
  python scripts/create_index_contract.py --clear-existing

  # Clear and rebuild specific district
  python scripts/create_index_contract.py --district A --clear-existing
        """
    )

    parser.add_argument('--district', type=str,
                       help='Specific district to process (A, B, C, ...). If not specified, processes all districts.')
    parser.add_argument('--tokenized-dir', type=str, default='data/tokenized_contract',
                       help='Base directory containing tokenized contract data (default: data/tokenized_contract)')
    parser.add_argument('--index-dir', type=str, default='data/contract_indexes',
                       help='Base directory for contract indexes (default: data/contract_indexes)')
    parser.add_argument('--clear-existing', action='store_true',
                       help='Clear existing indexes before creating new ones')

    args = parser.parse_args()

    # Validate tokenized directory
    if not os.path.exists(args.tokenized_dir):
        print(f"❌ Error: Tokenized directory does not exist: {args.tokenized_dir}")
        sys.exit(1)

    print("🚀 EOS Contract Index Creation Script")
    print("=" * 60)

    # Determine which districts to process
    if args.district:
        # Process specific district
        if args.district not in DISTRICT_NAMES:
            print(f"❌ Error: Unknown district: {args.district}")
            print(f"Valid districts: {', '.join(sorted(DISTRICT_NAMES.keys()))}")
            sys.exit(1)

        districts_to_process = [args.district]
    else:
        # Process all available districts
        districts_to_process = get_available_districts(args.tokenized_dir)

        if not districts_to_process:
            print(f"❌ Error: No district directories found in {args.tokenized_dir}")
            sys.exit(1)

    print(f"📂 Tokenized Data Directory: {args.tokenized_dir}")
    print(f"🗂️  Index Base Directory: {args.index_dir}")
    print(f"📊 Districts to process: {', '.join(districts_to_process)}")
    print()

    # Process each district
    overall_start = time.time()
    results = []

    for district in districts_to_process:
        result = process_district(district, args.tokenized_dir, args.index_dir, args.clear_existing)
        if result:
            results.append(result)

    # Overall summary
    overall_elapsed = time.time() - overall_start

    print("\n" + "=" * 60)
    print("📊 OVERALL SUMMARY")
    print("=" * 60)
    print(f"⏱️  Total time: {overall_elapsed:.2f} seconds")
    print(f"📦 Districts processed: {len(results)}/{len(districts_to_process)}")
    print()

    total_records = sum(r['total_records'] for r in results)
    total_added = sum(r['added_count'] for r in results)

    print("Per-district breakdown:")
    for result in results:
        print(f"  {result['district']} ({result['district_name']}): {result['final_count']} documents")

    print()
    print(f"📝 Total records processed: {total_records:,}")
    print(f"📄 Total documents added: {total_added:,}")

    if len(results) == len(districts_to_process):
        print("🎉 All contract indexes created successfully!")
    else:
        failed = len(districts_to_process) - len(results)
        print(f"⚠️  Completed with {failed} failed district(s)")

    print(f"💾 Indexes saved to: {args.index_dir}")


if __name__ == '__main__':
    main()
