#!/usr/bin/env python3
"""
Tokenization Script for EOS Search Engine

Tokenizes Japanese text content from CSV files or JSON folders and creates intermediate files
for index creation. Supports merging additional company information from DataFrames.

Usage:
    # From CSV file
    python scripts/tokenize_csv.py --csv-file <csv_file> [options]
    
    # From JSON folder with DataFrame merging
    python scripts/tokenize_csv.py --json-folder <json_folder> --dataframe-file <csv_file> [options]

Examples:
    python scripts/tokenize_csv.py --csv-file data/companies.csv --batch-size 1000
    python scripts/tokenize_csv.py --json-folder data/sample_companies/ --dataframe-file data/company_info.csv
"""

import argparse
import csv
import os
import sys
import time
import json
import glob
from typing import List, Dict, Tuple, Optional
from janome.tokenizer import Tokenizer
from multiprocessing import Pool, cpu_count, Manager
import multiprocessing as mp
import pandas as pd

# Add the parent directory to the path to import app modules
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


class JapaneseTokenizer:
    """Japanese text tokenizer using Janome"""
    
    def __init__(self):
        self.tokenizer = Tokenizer()
        # Common stop words to filter out
        self.stop_words = set([
            'する', 'ある', 'この', 'その', 'あの', 'という', 'といった', 'など', 'により',
            'について', 'において', 'に関して', 'に対して', 'として', 'による', 'から',
            'まで', 'では', 'には', 'にて', 'での', 'への', 'からの', 'までの'
        ])
    
    def tokenize_text(self, text: str) -> dict:
        """
        Tokenize Japanese text and return essential token information
        Returns processed tokens without verbose debugging details
        """
        if not text:
            return {
                'content_tokens': '',
                'token_count': 0
            }
        
        tokens = []
        
        for token in self.tokenizer.tokenize(text):
            word = token.surface.lower().strip()
            pos = token.part_of_speech.split(',')[0]
            
            # Include meaningful parts of speech
            if pos in ['名詞', '動詞', '形容詞', '副詞'] and len(word) > 1:
                if word not in self.stop_words:
                    tokens.append(word)
        
        return {
            'content_tokens': ' '.join(tokens),
            'token_count': len(tokens)
        }


def read_json_folder(json_folder: str, dataframe_file: Optional[str] = None) -> List[Dict]:
    """Read JSON files from folder and optionally merge with DataFrame"""
    print(f"📖 Reading JSON files from folder: {json_folder}")
    
    if not os.path.exists(json_folder):
        print(f"❌ Error: JSON folder does not exist: {json_folder}")
        return []
    
    # Find all JSON files in the folder
    json_files = glob.glob(os.path.join(json_folder, "*.json"))
    if not json_files:
        print(f"❌ Error: No JSON files found in {json_folder}")
        return []
    
    print(f"📁 Found {len(json_files)} JSON files")
    
    # Load DataFrame if provided and convert to dictionary for fast lookup
    df_dict = None
    if dataframe_file:
        try:
            df_data = pd.read_csv(dataframe_file)
            # Convert to dictionary with jcn as key for O(1) lookup
            df_data['jcn'] = df_data['jcn'].astype(str)
            df_dict = df_data.set_index('jcn').to_dict('index')
            print(f"📊 Loaded DataFrame with {len(df_data)} records from {dataframe_file}")
            print(f"🔑 Created lookup dictionary with {len(df_dict)} JCN keys")
        except Exception as e:
            print(f"⚠️  Warning: Could not load DataFrame: {e}")
            df_dict = None
    
    records = []
    total_files = len(json_files)
    
    for i, json_file in enumerate(json_files, 1):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)
            
            # Convert JSON structure to URL-based records (one per URL)
            url_records = convert_json_to_records(json_data, df_dict)
            records.extend(url_records)
            
            if i % 100 == 0:
                print(f"   📝 Processed {i}/{total_files} JSON files")
                
        except Exception as e:
            print(f"⚠️  Warning: Could not process {json_file}: {e}")
            continue
    
    print(f"✅ Successfully loaded {len(records)} records from JSON files")
    return records


def convert_json_to_records(json_data: Dict, df_dict: Optional[Dict] = None) -> List[Dict]:
    """Convert JSON structure to multiple URL-based records"""
    try:
        # Extract basic company information from JSON
        jcn = str(json_data.get('jcn', ''))
        if not jcn:
            return []
            
        # Base company information to be shared across all URL records
        base_info = {
            'jcn': jcn,
            'company_name_kj': json_data.get('company_name', {}).get('kj', ''),
            'company_address_all': json_data.get('company_address', {}).get('all', ''),
            'prefecture': json_data.get('company_address', {}).get('prefecture', ''),
            'city': json_data.get('company_address', {}).get('city', ''),
            'employee': json_data.get('company_info', {}).get('employee') or 0,
            'main_domain_url': json_data.get('homepage', {}).get('main_domain', {}).get('url', ''),
        }
        
        # Merge with DataFrame dictionary if provided (O(1) lookup)
        if df_dict is not None and jcn in df_dict:
            df_record = df_dict[jcn]
            # Merge additional fields from DataFrame
            for col, value in df_record.items():
                if col not in base_info and pd.notna(value):
                    base_info[col] = value
        
        records = []
        homepage = json_data.get('homepage', {})
        
        # Create record for main domain
        main_domain = homepage.get('main_domain', {})
        if main_domain.get('url'):
            main_record = base_info.copy()
            main_record.update({
                'id': f"{jcn}_main",
                'url': main_domain['url'],
                'url_name': 'メインサイト',
                'content': f"{base_info['company_name_kj']} {main_domain['url']}".strip()
            })
            records.append(main_record)
        
        # Create records for each sub-domain
        sub_domains = homepage.get('sub_domain', [])
        for i, sub_domain in enumerate(sub_domains):
            if sub_domain.get('url'):
                sub_record = base_info.copy()
                
                # Build content from tags
                tags = sub_domain.get('tags', [])
                content_parts = [base_info['company_name_kj']]
                content_parts.extend(tags)
                
                sub_record.update({
                    'id': f"{jcn}_sub_{i+1}",
                    'url': sub_domain['url'],
                    'url_name': ' '.join(tags) if tags else f'サブページ{i+1}',
                    'content': ' '.join(filter(None, content_parts))
                })
                records.append(sub_record)
        
        return records
        
    except Exception as e:
        print(f"⚠️  Warning: Error converting JSON record: {e}")
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


def process_batch_tokenization(tokenizer: JapaneseTokenizer, batch: List[Dict], batch_num: int) -> List[Dict]:
    """Process a batch of records and tokenize content"""
    print(f"🔄 Tokenizing batch {batch_num} ({len(batch)} records)...")
    
    tokenized_records = []
    start_time = time.time()
    
    for i, record in enumerate(batch):
        # Tokenize the content field
        content_analysis = tokenizer.tokenize_text(record.get('content', ''))
        
        # Create tokenized record
        tokenized_record = record.copy()  # Keep all original fields
        
        # Add tokenization results
        tokenized_record['content_tokens'] = content_analysis['content_tokens']
        tokenized_record['token_count'] = content_analysis['token_count']
        
        # Remove original content to save space (keeping only tokenized version)
        if 'content' in tokenized_record:
            del tokenized_record['content']
        
        tokenized_records.append(tokenized_record)
        
        # Progress indicator for large batches
        if len(batch) > 100 and (i + 1) % 100 == 0:
            print(f"   📝 Processed {i + 1}/{len(batch)} records in batch {batch_num}")
    
    elapsed = time.time() - start_time
    print(f"✅ Batch {batch_num} tokenized in {elapsed:.2f} seconds")
    
    return tokenized_records


def save_tokenized_batch(tokenized_records: List[Dict], output_dir: str, batch_num: int) -> str:
    """Save tokenized records to intermediate file"""
    filename = f"tokenized_batch_{batch_num:04d}.json"
    filepath = os.path.join(output_dir, filename)
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            json.dump(tokenized_records, f, ensure_ascii=False, indent=2)
        
        print(f"💾 Saved batch {batch_num} to {filename}")
        return filepath
        
    except Exception as e:
        print(f"❌ Error saving batch {batch_num}: {e}")
        return None


def create_processing_summary(output_dir: str, total_batches: int, total_records: int, processing_time: float) -> str:
    """Create a summary file of the tokenization process"""
    summary_file = os.path.join(output_dir, "tokenization_summary.json")
    
    summary = {
        'processing_info': {
            'total_batches': total_batches,
            'total_records': total_records,
            'processing_time_seconds': round(processing_time, 2),
            'records_per_second': round(total_records / processing_time, 2) if processing_time > 0 else 0,
            'created_at': time.strftime('%Y-%m-%d %H:%M:%S')
        },
        'file_info': {
            'batch_files': [f"tokenized_batch_{i:04d}.json" for i in range(1, total_batches + 1)],
            'format': 'json',
            'encoding': 'utf-8'
        },
        'tokenization_settings': {
            'included_pos': ['名詞', '動詞', '形容詞', '副詞'],
            'min_word_length': 2,
            'stop_words_filtered': True,
            'tokenizer': 'janome'
        }
    }
    
    try:
        with open(summary_file, 'w', encoding='utf-8') as f:
            json.dump(summary, f, ensure_ascii=False, indent=2)
        
        print(f"📋 Processing summary saved to tokenization_summary.json")
        return summary_file
        
    except Exception as e:
        print(f"⚠️  Warning: Could not save summary: {e}")
        return None


def get_output_dir(csv_file: str = None, json_folder: str = None, output_dir: str = None) -> str:
    """Generate output directory based on input source"""
    if output_dir:
        # User specified explicit output directory
        return output_dir
    
    if json_folder:
        # Auto-generate from JSON folder name
        folder_name = os.path.basename(json_folder.rstrip('/'))
        return f"data/{folder_name}/tokenized"
    elif csv_file:
        # Auto-generate from CSV filename
        csv_name = os.path.splitext(os.path.basename(csv_file))[0]
        return f"data/{csv_name}/tokenized"
    else:
        # Fallback
        return "data/tokenized"


def main():
    parser = argparse.ArgumentParser(
        description='Tokenize Japanese text from CSV files or JSON folders for index creation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # From CSV file
  python scripts/tokenize_csv.py --csv-file data/companies.csv
  python scripts/tokenize_csv.py --csv-file data/large_dataset.csv --batch-size 1000
  
  # From JSON folder with DataFrame merging
  python scripts/tokenize_csv.py --json-folder data/sample_companies/ --dataframe-file data/company_info.csv
  python scripts/tokenize_csv.py --json-folder data/companies_json/ --output-dir data/custom/
        """
    )
    
    # Input source - either CSV file or JSON folder
    input_group = parser.add_mutually_exclusive_group(required=True)
    input_group.add_argument('--csv-file', type=str, help='Path to CSV file containing enterprise data')
    input_group.add_argument('--json-folder', type=str, help='Path to folder containing JSON files with company data')
    
    parser.add_argument('--dataframe-file', type=str, 
                       help='Path to CSV file with additional company information to merge (used with --json-folder)')
    parser.add_argument('--batch-size', type=int, default=500, 
                       help='Number of records to process per batch (default: 500)')
    parser.add_argument('--output-dir', type=str,
                       help='Directory for tokenized output files. If not specified, auto-generates based on input source')
    parser.add_argument('--clear-output', action='store_true',
                       help='Clear output directory before processing')
    
    args = parser.parse_args()
    
    # Validate arguments
    if args.csv_file and not os.path.exists(args.csv_file):
        print(f"❌ Error: CSV file does not exist: {args.csv_file}")
        sys.exit(1)
        
    if args.json_folder and not os.path.exists(args.json_folder):
        print(f"❌ Error: JSON folder does not exist: {args.json_folder}")
        sys.exit(1)
        
    if args.dataframe_file and not os.path.exists(args.dataframe_file):
        print(f"❌ Error: DataFrame file does not exist: {args.dataframe_file}")
        sys.exit(1)
        
    if args.dataframe_file and not args.json_folder:
        print("❌ Error: --dataframe-file can only be used with --json-folder")
        sys.exit(1)
    
    if args.batch_size <= 0:
        print("❌ Error: Batch size must be a positive integer")
        sys.exit(1)
    
    # Determine output directory
    output_dir = get_output_dir(args.csv_file, args.json_folder, args.output_dir)
    
    print("🔄 EOS Tokenization Script")
    print("=" * 50)
    if args.csv_file:
        print(f"📂 Input: CSV File - {args.csv_file}")
    else:
        print(f"📂 Input: JSON Folder - {args.json_folder}")
        if args.dataframe_file:
            print(f"📊 DataFrame: {args.dataframe_file}")
    print(f"📦 Batch Size: {args.batch_size}")
    print(f"📁 Output Directory: {output_dir}")
    print()
    
    # Setup output directory
    if args.clear_output and os.path.exists(output_dir):
        import shutil
        print(f"🗑️  Clearing output directory: {output_dir}")
        shutil.rmtree(output_dir)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"📁 Created output directory: {output_dir}")
    
    # Initialize tokenizer
    print("🔧 Initializing Japanese tokenizer...")
    tokenizer = JapaneseTokenizer()
    print("✅ Tokenizer ready")
    print()
    
    # Read input data
    start_time = time.time()
    if args.csv_file:
        # Read CSV file in batches
        batches = read_csv_batch(args.csv_file, args.batch_size)
        input_type = "CSV"
    else:
        # Read JSON folder and create batches
        records = read_json_folder(args.json_folder, args.dataframe_file)
        if not records:
            print("❌ No data to process. Exiting.")
            sys.exit(1)
        
        # Create batches from records
        batches = []
        for i in range(0, len(records), args.batch_size):
            batch = records[i:i + args.batch_size]
            batches.append(batch)
        input_type = "JSON"
    
    if not batches:
        print(f"❌ No {input_type.lower()} data to process. Exiting.")
        sys.exit(1)
    
    total_records = sum(len(batch) for batch in batches)
    
    print(f"🔄 Starting tokenization...")
    print(f"📊 Total records: {total_records}")
    print(f"📦 Total batches: {len(batches)}")
    print(f"📝 Input type: {input_type}")
    print()
    
    # Process each batch
    successful_batches = 0
    for i, batch in enumerate(batches, 1):
        # Tokenize batch
        tokenized_records = process_batch_tokenization(tokenizer, batch, i)
        
        if tokenized_records:
            # Save tokenized batch
            saved_file = save_tokenized_batch(tokenized_records, output_dir, i)
            if saved_file:
                successful_batches += 1
        
        # Show progress
        progress = (i / len(batches)) * 100
        print(f"📈 Progress: {progress:.1f}% ({i}/{len(batches)} batches)")
        print()
    
    # Final statistics
    elapsed_total = time.time() - start_time
    
    print("=" * 50)
    print("📊 TOKENIZATION COMPLETE")
    print("=" * 50)
    print(f"⏱️  Total time: {elapsed_total:.2f} seconds")
    print(f"✅ Successful batches: {successful_batches}/{len(batches)}")
    print(f"📝 Records processed: {total_records}")
    print(f"📁 Output directory: {output_dir}")
    
    # Create summary file
    create_processing_summary(output_dir, len(batches), total_records, elapsed_total)
    
    if successful_batches == len(batches):
        print("🎉 Tokenization completed successfully!")
        print()
        print("📋 Next steps:")
        if args.csv_file:
            print(f"   python scripts/create_index.py --tokenized-dir {output_dir}")
        else:
            print(f"   python scripts/create_index.py --tokenized-dir {output_dir}")
            print(f"   # Tokenized from JSON folder: {args.json_folder}")
            if args.dataframe_file:
                print(f"   # Merged with DataFrame: {args.dataframe_file}")
    else:
        failed_batches = len(batches) - successful_batches
        print(f"⚠️  Tokenization completed with {failed_batches} failed batches")
    
    # Performance metrics
    if total_records > 0:
        records_per_second = total_records / elapsed_total
        print(f"⚡ Processing rate: {records_per_second:.1f} records/second")


if __name__ == '__main__':
    main()