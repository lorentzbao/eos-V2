#!/usr/bin/env python3
"""
CSV Tokenization Script for EOS Search Engine

Tokenizes Japanese text content in CSV files and creates intermediate files
for index creation. This allows for preprocessing, debugging, and reusing
tokenized data without re-tokenizing.

Usage:
    python scripts/tokenize_csv.py <csv_file> [--batch-size BATCH_SIZE] [--output-dir OUTPUT_DIR]

Example:
    python scripts/tokenize_csv.py data/companies.csv --batch-size 1000
    python scripts/tokenize_csv.py data/companies.csv --output-dir data/tokenized/
"""

import argparse
import csv
import os
import sys
import time
import json
from typing import List, Dict, Tuple
from janome.tokenizer import Tokenizer
from multiprocessing import Pool, cpu_count, Manager
import multiprocessing as mp

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


def main():
    parser = argparse.ArgumentParser(
        description='Tokenize Japanese text in CSV files for index creation',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/tokenize_csv.py data/companies.csv
  python scripts/tokenize_csv.py data/large_dataset.csv --batch-size 1000
  python scripts/tokenize_csv.py data/test.csv --output-dir data/tokenized/
        """
    )
    
    parser.add_argument('csv_file', help='Path to CSV file containing enterprise data')
    parser.add_argument('--batch-size', type=int, default=500, 
                       help='Number of records to process per batch (default: 500)')
    parser.add_argument('--output-dir', type=str, default='data/tokenized',
                       help='Directory for tokenized output files (default: data/tokenized)')
    parser.add_argument('--clear-output', action='store_true',
                       help='Clear output directory before processing')
    
    args = parser.parse_args()
    
    # Validate arguments
    if not os.path.exists(args.csv_file):
        print(f"❌ Error: CSV file does not exist: {args.csv_file}")
        sys.exit(1)
    
    if args.batch_size <= 0:
        print("❌ Error: Batch size must be a positive integer")
        sys.exit(1)
    
    print("🔄 EOS CSV Tokenization Script")
    print("=" * 50)
    print(f"📂 Input CSV: {args.csv_file}")
    print(f"📦 Batch Size: {args.batch_size}")
    print(f"📁 Output Directory: {args.output_dir}")
    print()
    
    # Setup output directory
    if args.clear_output and os.path.exists(args.output_dir):
        import shutil
        print(f"🗑️  Clearing output directory: {args.output_dir}")
        shutil.rmtree(args.output_dir)
    
    if not os.path.exists(args.output_dir):
        os.makedirs(args.output_dir)
        print(f"📁 Created output directory: {args.output_dir}")
    
    # Initialize tokenizer
    print("🔧 Initializing Japanese tokenizer...")
    tokenizer = JapaneseTokenizer()
    print("✅ Tokenizer ready")
    print()
    
    # Read CSV file in batches
    start_time = time.time()
    batches = read_csv_batch(args.csv_file, args.batch_size)
    
    if not batches:
        print("❌ No data to process. Exiting.")
        sys.exit(1)
    
    total_records = sum(len(batch) for batch in batches)
    
    print(f"🔄 Starting tokenization...")
    print(f"📊 Total records: {total_records}")
    print(f"📦 Total batches: {len(batches)}")
    print()
    
    # Process each batch
    successful_batches = 0
    for i, batch in enumerate(batches, 1):
        # Tokenize batch
        tokenized_records = process_batch_tokenization(tokenizer, batch, i)
        
        if tokenized_records:
            # Save tokenized batch
            saved_file = save_tokenized_batch(tokenized_records, args.output_dir, i)
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
    print(f"📁 Output directory: {args.output_dir}")
    
    # Create summary file
    create_processing_summary(args.output_dir, len(batches), total_records, elapsed_total)
    
    if successful_batches == len(batches):
        print("🎉 Tokenization completed successfully!")
        print()
        print("📋 Next steps:")
        print(f"   python scripts/create_index.py --tokenized-dir {args.output_dir}")
    else:
        failed_batches = len(batches) - successful_batches
        print(f"⚠️  Tokenization completed with {failed_batches} failed batches")
    
    # Performance metrics
    if total_records > 0:
        records_per_second = total_records / elapsed_total
        print(f"⚡ Processing rate: {records_per_second:.1f} records/second")


if __name__ == '__main__':
    main()