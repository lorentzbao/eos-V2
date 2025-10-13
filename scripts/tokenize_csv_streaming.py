#!/usr/bin/env python3
"""
Tokenization Script for EOS Search Engine

Tokenizes Japanese text content from CSV files or JSON folders and creates intermediate files
for index creation. Supports merging additional company information from DataFrames.

Usage:
    # Basic usage with command-line overrides (like run.py)
    uv run python scripts/tokenize_csv.py input.csv_file=data/sample_companies.csv
    uv run python scripts/tokenize_csv.py input.json_folder=data/test_json_companies
    
    # Override processing settings
    uv run python scripts/tokenize_csv.py input.csv_file=data/sample.csv processing.batch_size=1000
    
    # Use configuration presets (optional)
    uv run python scripts/tokenize_csv.py --config-name tokenize_json
    uv run python scripts/tokenize_csv.py --config-name tokenize_csv

Examples:
    # Process CSV file
    uv run python scripts/tokenize_csv.py input.csv_file=data/sample_companies.csv
    
    # Process JSON folder with DataFrame merging
    uv run python scripts/tokenize_csv.py input.json_folder=data/test_json_companies input.dataframe_file=data/test_company_info.csv
    
    # Enable high-performance processing
    uv run python scripts/tokenize_csv.py input.json_folder=data/companies processing.use_hybrid_pipeline=true processing.num_processes=8
"""

import hydra
from omegaconf import DictConfig, OmegaConf
import os
import sys
import csv
import time
import json
import glob
import asyncio
from concurrent.futures import ThreadPoolExecutor, ProcessPoolExecutor, as_completed
from queue import Queue, Empty
from threading import Thread
from typing import List, Dict, Tuple, Optional, NamedTuple
from multiprocessing import Pool, cpu_count, Manager, Process
import multiprocessing as mp
import pandas as pd
from bs4 import BeautifulSoup

from bs4 import XMLParsedAsHTMLWarning
import warnings
warnings.filterwarnings("ignore", category=XMLParsedAsHTMLWarning)


# Data structures for pipeline processing
class FileTask(NamedTuple):
    """Task for file I/O operations"""
    file_path: str
    task_type: str  # 'json', 'html', 'csv'
    max_length: Optional[int] = None
    

class ProcessingTask(NamedTuple):
    """Task for CPU-intensive processing"""
    content: str
    task_type: str  # 'html_parse', 'tokenize'
    metadata: Dict
    max_length: Optional[int] = None


class ProcessedResult(NamedTuple):
    """Result from processing pipeline"""
    task_id: str
    content: str
    metadata: Dict
    processing_time: float


class JapaneseTokenizer:
    """Japanese text tokenizer using modular tokenizer backend"""

    def __init__(self, tokenizer_type: Optional[str] = None):
        """
        Initialize tokenizer with configurable backend.

        Args:
            tokenizer_type: Type of tokenizer ('janome', 'mecab', or None for auto-detect)
        """
        self.tokenizer = get_tokenizer(tokenizer_type)

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

        # Use the tokenizer's built-in filtering
        tokens = self.tokenizer.tokenize_and_filter(text, min_length=2)

        # Additional filtering for numeric tokens
        filtered_tokens = [
            token.lower().strip()
            for token in tokens
            if not token.isdigit()
        ]

        return {
            'content_tokens': ' '.join(filtered_tokens),
            'token_count': len(filtered_tokens)
        }


def build_company_records(json_data: Dict, df_dict: Optional[Dict], parsed_html_contents: Dict[str, str],
                         max_subdomains_per_company: int = None) -> List[Dict]:
    """Build records for a single company using pre-parsed HTML content

    Args:
        json_data: Company JSON data
        df_dict: DataFrame dictionary for merging additional info
        parsed_html_contents: Dictionary mapping html_path -> parsed_content
        max_subdomains_per_company: Maximum number of sub-domains to process

    Returns:
        List of URL-based records for this company
    """
    try:
        jcn = str(json_data.get('jcn', ''))
        if not jcn:
            return []

        # Base company information
        base_info = {
            'jcn': jcn,
            'company_name_kj': json_data.get('company_name', {}).get('kj', ''),
            'company_address_all': json_data.get('company_address', {}).get('all', ''),
            'prefecture': json_data.get('company_address', {}).get('prefecture', ''),
            'city': json_data.get('company_address', {}).get('city', ''),
            'main_domain_url': json_data.get('homepage', {}).get('main_domain', {}).get('url', ''),
        }

        # Merge DataFrame data
        if df_dict is not None and jcn in df_dict:
            df_record = df_dict[jcn]
            for col, value in df_record.items():
                if col not in base_info and pd.notna(value):
                    base_info[col] = value

        homepage = json_data.get('homepage', {})
        records = []

        # Main domain
        main_domain = homepage.get('main_domain', {})
        if main_domain.get('url'):
            html_path = main_domain.get('html_path', '')
            html_content = parsed_html_contents.get(html_path, '') if html_path else ''

            content_parts = [base_info['company_name_kj']]
            if html_content:
                content_parts.append(html_content)
            else:
                content_parts.append(main_domain['url'])

            record = base_info.copy()
            record.update({
                'id': f"{jcn}_main",
                'url': main_domain['url'],
                'url_name': 'メインサイト',
                'content': ' '.join(filter(None, content_parts))
            })
            records.append(record)

        # Sub-domains
        sub_domains = homepage.get('sub_domain', [])
        if max_subdomains_per_company is not None:
            sub_domains = sub_domains[:max_subdomains_per_company]

        for i, sub_domain in enumerate(sub_domains):
            if sub_domain.get('url'):
                html_path = sub_domain.get('html_path', '')
                html_content = parsed_html_contents.get(html_path, '') if html_path else ''

                content_parts = [base_info['company_name_kj']]
                if html_content:
                    content_parts.append(html_content)
                else:
                    content_parts.extend(sub_domain.get('tags', []))

                record = base_info.copy()
                record.update({
                    'id': f"{jcn}_sub_{i + 1}",
                    'url': sub_domain['url'],
                    'url_name': ' '.join(sub_domain.get('tags', [])) if sub_domain.get('tags') else f"サブページ{i + 1}",
                    'content': ' '.join(filter(None, content_parts))
                })
                records.append(record)

        return records
    except Exception as e:
        print(f"⚠️  Warning: Error building records for company: {e}")
        return []


def io_worker(paths_queue: Queue, html_queue: Queue, primary_root_path: str, secondary_root_path: str):
    """I/O worker thread - reads HTML files and puts them in queue"""
    while True:
        path = paths_queue.get()
        if path is None:  # Poison pill
            break

        try:
            file_path, content = read_file_sync(path, 'utf-8', primary_root_path, secondary_root_path)
            # Use original path, not file_path which might be normalized
            html_queue.put((path, content))
        except Exception as e:
            print(f"⚠️ Warning: Error reading {path}: {e}")
            html_queue.put((path, ""))
        finally:
            paths_queue.task_done()


def cpu_worker(html_queue, output_queue, max_content_length: int, num_files: int):
    """CPU worker process - parses HTML from queue and outputs results (OLD 2-stage version)

    Note: Queue types are not typed here because multiprocessing.Manager().Queue()
    returns a different type than queue.Queue
    """
    while True:
        try:
            item = html_queue.get(timeout=1)
            if item is None:  # Poison pill
                break

            path, content = item
            if content:
                parsed = parse_html_content_cpu(content, max_content_length)
            else:
                parsed = ""

            output_queue.put((path, parsed))
        except:
            # Catch timeout or any other exceptions
            continue


def cpu_worker_with_tokenization(html_queue, record_queue, path_to_record_map,
                                 max_content_length: int, tokenizer_config):
    """CPU worker for 3-stage pipeline: parse HTML + tokenize + build complete records

    This worker does the heavy CPU work:
    1. Parse HTML with BeautifulSoup
    2. Build complete record with company metadata
    3. Tokenize Japanese text with Janome/MeCab
    4. Send tokenized record to writer

    Args:
        html_queue: Input queue with (path, html_content) tuples
        record_queue: Output queue for tokenized records ready to write
        path_to_record_map: Mapping of html_path -> (jcn, domain_type, index, base_info, url, url_name)
        max_content_length: Maximum HTML content length
        tokenizer_config: Tokenizer configuration dict
    """
    print(f"  [CPU Worker] Starting, have {len(path_to_record_map)} paths in map")

    # Initialize tokenizer in this worker process
    try:
        tokenizer = JapaneseTokenizer(tokenizer_type=tokenizer_config.get('type'))
        print(f"  [CPU Worker] Tokenizer initialized")
    except Exception as e:
        print(f"  [CPU Worker] ERROR initializing tokenizer: {e}")
        import traceback
        traceback.print_exc()
        return

    processed_count = 0
    while True:
        try:
            item = html_queue.get(timeout=1)
            if item is None:  # Poison pill
                print(f"  [CPU Worker] Processed {processed_count} files, shutting down")
                break

            path, html_content = item

            # Skip if path not in mapping (this shouldn't happen but handle gracefully)
            if path not in path_to_record_map:
                print(f"⚠️ Warning: Path {path} not found in record map")
                continue

            # Step 1: Parse HTML (CPU intensive)
            if html_content:
                parsed_text = parse_html_content_cpu(html_content, max_content_length)
            else:
                parsed_text = ""

            # Step 2: Build complete record with metadata
            jcn, domain_type, index, base_info, url, url_name = path_to_record_map[path]

            # Build content (company name + parsed HTML text)
            content_parts = [base_info.get('company_name_kj', '')]
            if parsed_text:
                content_parts.append(parsed_text)
            else:
                content_parts.append(url)

            content = ' '.join(filter(None, content_parts))

            # Step 3: Tokenize content (CPU intensive)
            tokenized = tokenizer.tokenize_text(content)

            # Step 4: Build final tokenized record
            record = base_info.copy()
            record.update({
                'id': f"{jcn}_{domain_type}_{index}" if domain_type == 'sub' else f"{jcn}_main",
                'url': url,
                'url_name': url_name,
                'content_tokens': tokenized['content_tokens'],
                'token_count': tokenized['token_count']
            })

            # Send to writer (no 'content' field - already tokenized!)
            record_queue.put(record)
            processed_count += 1

        except Exception as e:
            # Log error but continue processing
            if 'path' in locals():
                print(f"⚠️ Warning: Error processing {path}: {e}")
            import traceback
            traceback.print_exc()
            continue


def writer_worker(record_queue, output_dir, batch_size, progress_queue=None):
    """Writer process for 3-stage pipeline: batch records and write to disk

    This worker does lightweight I/O:
    1. Collect records into batches
    2. Write JSON files to disk
    3. Report progress

    Args:
        record_queue: Input queue with tokenized records
        output_dir: Output directory for batch files
        batch_size: Number of records per batch file
        progress_queue: Optional queue for progress reporting
    """
    import json
    import time

    current_batch = []
    batch_num = 1
    total_written = 0
    start_time = time.time()

    while True:
        try:
            record = record_queue.get(timeout=1)
            if record is None:  # Poison pill
                break

            current_batch.append(record)

            # Write batch when full
            if len(current_batch) >= batch_size:
                batch_file = os.path.join(output_dir, f"tokenized_batch_{batch_num:04d}.json")
                with open(batch_file, 'w', encoding='utf-8') as f:
                    json.dump(current_batch, f, ensure_ascii=False, indent=2)

                total_written += len(current_batch)
                elapsed = time.time() - start_time
                rate = total_written / elapsed if elapsed > 0 else 0

                print(f"💾 Wrote batch {batch_num}: {len(current_batch)} records ({rate:.1f} records/sec)")

                # Report progress if queue provided
                if progress_queue:
                    progress_queue.put({
                        'batch_num': batch_num,
                        'records_written': total_written,
                        'rate': rate
                    })

                current_batch = []
                batch_num += 1

        except:
            continue

    # Write remaining records
    if current_batch:
        batch_file = os.path.join(output_dir, f"tokenized_batch_{batch_num:04d}.json")
        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(current_batch, f, ensure_ascii=False, indent=2)

        total_written += len(current_batch)
        print(f"💾 Wrote final batch {batch_num}: {len(current_batch)} records")

        if progress_queue:
            progress_queue.put({
                'batch_num': batch_num,
                'records_written': total_written,
                'rate': 0
            })

    elapsed_total = time.time() - start_time
    avg_rate = total_written / elapsed_total if elapsed_total > 0 else 0
    print(f"✅ Writer finished: {total_written} records in {elapsed_total:.1f}s ({avg_rate:.1f} records/sec avg)")


def read_json_folder_streaming(json_files: List[str], df_dict: Optional[Dict], max_content_length: int,
                               num_processes: int, max_concurrent_io: int, primary_root_path: str,
                               secondary_root_path: str, max_subdomains_per_company: int = None) -> List[Dict]:
    """Streaming pipeline - I/O and CPU processing run concurrently with queue-based communication

    This implements a producer-consumer pattern where I/O threads continuously feed HTML content
    to CPU processes via queues, eliminating idle time and maximizing resource utilization.

    Args:
        json_files: List of JSON file paths
        df_dict: DataFrame dictionary for merging
        max_content_length: Max HTML content length
        num_processes: Number of CPU processes for HTML parsing
        max_concurrent_io: Number of I/O threads for file reading
        primary_root_path: Primary root path for HTML files
        secondary_root_path: Secondary root path for HTML files
        max_subdomains_per_company: Max sub-domains per company

    Returns:
        List of all records from all companies
    """
    total_files = len(json_files)
    print(f"Stage 1/3: Loading {total_files} JSON files...")

    # Step 1: Load all JSON files and collect HTML paths (unchanged)
    all_json_data = []
    all_html_paths = []

    for i, json_file in enumerate(json_files, 1):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            jcn = str(json_data.get('jcn', ''))
            if not jcn:
                continue

            all_json_data.append(json_data)

            # Collect HTML paths from this company
            homepage = json_data.get('homepage', {})

            # Main domain
            main_domain = homepage.get('main_domain', {})
            if main_domain.get('html_path'):
                all_html_paths.append(main_domain['html_path'])

            # Sub-domains (with limit)
            sub_domains = homepage.get('sub_domain', [])
            if max_subdomains_per_company is not None:
                sub_domains = sub_domains[:max_subdomains_per_company]

            for sub_domain in sub_domains:
                if sub_domain.get('html_path'):
                    all_html_paths.append(sub_domain['html_path'])

            if i % 100 == 0:
                print(f"   📝 Loaded {i}/{total_files} JSON files")

        except Exception as e:
            print(f"⚠️ Warning: Could not load {json_file}: {e}")
            continue

    # Remove duplicate paths
    unique_html_paths = list(set(all_html_paths))
    print(f"✅ Loaded {len(all_json_data)} companies with {len(unique_html_paths)} unique HTML files")

    # Step 2/3: STREAMING PIPELINE - I/O and CPU run concurrently
    if not num_processes:
        num_processes = cpu_count()

    print(f"Stage 2/3: Reading and parsing {len(unique_html_paths)} HTML files...")
    print(f"  Pipeline: {max_concurrent_io} I/O threads → Queue(100) → {num_processes} CPU processes")

    start_time = time.time()
    parsed_contents = {}

    if unique_html_paths:
        # Create multiprocessing-safe queues
        manager = Manager()
        paths_queue = manager.Queue()
        html_queue = manager.Queue(maxsize=100)  # Bounded queue to control memory
        output_queue = manager.Queue()

        # Populate paths queue
        for path in unique_html_paths:
            paths_queue.put(path)

        # Add poison pills for I/O workers
        for _ in range(max_concurrent_io):
            paths_queue.put(None)

        # Start I/O threads
        io_threads = []
        for _ in range(max_concurrent_io):
            t = Thread(target=io_worker, args=(paths_queue, html_queue, primary_root_path, secondary_root_path))
            t.start()
            io_threads.append(t)

        # Start CPU processes
        with ProcessPoolExecutor(max_workers=num_processes) as cpu_executor:
            cpu_futures = []
            for _ in range(num_processes):
                future = cpu_executor.submit(cpu_worker, html_queue, output_queue, max_content_length, len(unique_html_paths))
                cpu_futures.append(future)

            # Collect results with progress tracking
            completed = 0
            while completed < len(unique_html_paths):
                try:
                    path, parsed = output_queue.get(timeout=1)
                    parsed_contents[path] = parsed
                    completed += 1

                    if completed % 500 == 0:
                        elapsed = time.time() - start_time
                        rate = completed / elapsed if elapsed > 0 else 0
                        print(f"   📝 Processed {completed}/{len(unique_html_paths)} files ({rate:.1f} files/sec)")

                except:
                    continue

            # Wait for I/O threads to finish
            for t in io_threads:
                t.join()

            # Send poison pills to CPU workers
            for _ in range(num_processes):
                html_queue.put(None)

        elapsed_total = time.time() - start_time
        avg_rate = len(unique_html_paths) / elapsed_total if elapsed_total > 0 else 0
        print(f"✅ Processed {len(parsed_contents)} HTML files in {elapsed_total:.1f} seconds ({avg_rate:.1f} files/sec avg)")

    # Step 4: Build final records using pre-processed content (unchanged)
    print(f"Building records for {len(all_json_data)} companies...")
    all_records = []

    for i, json_data in enumerate(all_json_data, 1):
        company_records = build_company_records(json_data, df_dict, parsed_contents, max_subdomains_per_company)
        all_records.extend(company_records)

        if i % 100 == 0:
            print(f"   📝 Built records for {i}/{len(all_json_data)} companies")

    print(f"✅ Successfully loaded {len(all_records)} records from {len(all_json_data)} companies")
    return all_records


def read_json_folder_3stage_pipeline(json_files: List[str], df_dict: Optional[Dict], max_content_length: int,
                                     num_cpu_workers: int, max_concurrent_io: int, primary_root_path: str,
                                     secondary_root_path: str, max_subdomains_per_company: int,
                                     tokenizer_config: Dict, output_dir: str, batch_size: int) -> int:
    """3-stage streaming pipeline: I/O → CPU+Tokenize → Writer

    This implements true streaming with constant memory usage:
    - Stage 1: I/O threads read HTML files
    - Stage 2: CPU processes parse HTML, tokenize text, build complete records
    - Stage 3: Writer process batches and writes to disk

    All three stages run concurrently with queue-based communication.
    No accumulation of records in memory - constant memory footprint!

    Args:
        json_files: List of JSON file paths
        df_dict: DataFrame dictionary for merging
        max_content_length: Max HTML content length
        num_cpu_workers: Number of CPU worker processes for Stage 2
        max_concurrent_io: Number of I/O threads for Stage 1
        primary_root_path: Primary root path for HTML files
        secondary_root_path: Secondary root path for HTML files
        max_subdomains_per_company: Max sub-domains per company
        tokenizer_config: Tokenizer configuration dict
        output_dir: Output directory for batch files
        batch_size: Records per batch file

    Returns:
        Total number of records processed
    """
    total_files = len(json_files)
    print(f"Stage 1/3: Loading {total_files} JSON files...")

    # Step 1: Load JSON metadata and build path-to-record mapping
    all_json_data = []
    all_html_paths = []
    path_to_record_map = {}  # html_path -> (jcn, domain_type, index, base_info, url, url_name)

    for i, json_file in enumerate(json_files, 1):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            jcn = str(json_data.get('jcn', ''))
            if not jcn:
                continue

            all_json_data.append(json_data)

            # Build base company info
            base_info = {
                'jcn': jcn,
                'company_name_kj': json_data.get('company_name', {}).get('kj', ''),
                'company_address_all': json_data.get('company_address', {}).get('all', ''),
                'prefecture': json_data.get('company_address', {}).get('prefecture', ''),
                'city': json_data.get('company_address', {}).get('city', ''),
                'main_domain_url': json_data.get('homepage', {}).get('main_domain', {}).get('url', ''),
            }

            # Merge DataFrame data (convert to simple Python types for pickling)
            if df_dict is not None and jcn in df_dict:
                df_record = df_dict[jcn]
                for col, value in df_record.items():
                    if col not in base_info and pd.notna(value):
                        # Convert to native Python type for pickling
                        if hasattr(value, 'item'):  # numpy/pandas scalar
                            base_info[col] = value.item()
                        else:
                            base_info[col] = value

            homepage = json_data.get('homepage', {})

            # Map main domain
            main_domain = homepage.get('main_domain', {})
            if main_domain.get('html_path'):
                html_path = main_domain['html_path']
                all_html_paths.append(html_path)
                path_to_record_map[html_path] = (
                    jcn, 'main', 0, base_info,
                    main_domain.get('url', ''),
                    'メインサイト'
                )

            # Map sub-domains
            sub_domains = homepage.get('sub_domain', [])
            if max_subdomains_per_company is not None:
                sub_domains = sub_domains[:max_subdomains_per_company]

            for idx, sub_domain in enumerate(sub_domains):
                if sub_domain.get('html_path'):
                    html_path = sub_domain['html_path']
                    all_html_paths.append(html_path)
                    url_name = ' '.join(sub_domain.get('tags', [])) if sub_domain.get('tags') else f"サブページ{idx + 1}"
                    path_to_record_map[html_path] = (
                        jcn, 'sub', idx + 1, base_info,
                        sub_domain.get('url', ''),
                        url_name
                    )

            if i % 100 == 0:
                print(f"   📝 Loaded {i}/{total_files} JSON files")

        except Exception as e:
            print(f"⚠️ Warning: Could not load {json_file}: {e}")
            continue

    # Remove duplicate paths
    unique_html_paths = list(set(all_html_paths))
    print(f"✅ Loaded {len(all_json_data)} companies with {len(unique_html_paths)} unique HTML files")
    print(f"   path_to_record_map has {len(path_to_record_map)} entries")
    if len(path_to_record_map) > 0:
        sample_path = list(path_to_record_map.keys())[0]
        print(f"   Sample path in map: {sample_path}")
        # Test pickling
        import pickle
        try:
            pickled_size = len(pickle.dumps(path_to_record_map))
            print(f"   path_to_record_map pickle size: {pickled_size} bytes")
        except Exception as e:
            print(f"   ⚠️ Cannot pickle path_to_record_map: {e}")

    # Step 2/3: 3-STAGE STREAMING PIPELINE
    if not num_cpu_workers:
        num_cpu_workers = cpu_count()

    print(f"\nStage 2/3: 3-Stage Streaming Pipeline")
    print(f"  Stage 1: {max_concurrent_io} I/O threads (read HTML)")
    print(f"  Stage 2: {num_cpu_workers} CPU workers (parse + tokenize)")
    print(f"  Stage 3: 1 writer process (batch + write)")
    print(f"  Processing {len(unique_html_paths)} files...\n")

    start_time = time.time()

    if unique_html_paths:
        # Create multiprocessing-safe queues
        manager = Manager()
        paths_queue = manager.Queue()
        html_queue = manager.Queue(maxsize=100)      # Stage 1 → Stage 2
        record_queue = manager.Queue(maxsize=500)    # Stage 2 → Stage 3

        # Populate paths queue
        for path in unique_html_paths:
            paths_queue.put(path)

        # Add poison pills for I/O workers
        for _ in range(max_concurrent_io):
            paths_queue.put(None)

        # Start Stage 1: I/O threads
        io_threads = []
        for _ in range(max_concurrent_io):
            t = Thread(target=io_worker, args=(paths_queue, html_queue, primary_root_path, secondary_root_path))
            t.start()
            io_threads.append(t)

        # Start Stage 3: Writer process
        writer_process = Process(
            target=writer_worker,
            args=(record_queue, output_dir, batch_size, None)
        )
        writer_process.start()

        # Start Stage 2: CPU processes
        with ProcessPoolExecutor(max_workers=num_cpu_workers) as cpu_executor:
            cpu_futures = []
            for _ in range(num_cpu_workers):
                future = cpu_executor.submit(
                    cpu_worker_with_tokenization,
                    html_queue,
                    record_queue,
                    path_to_record_map,
                    max_content_length,
                    tokenizer_config
                )
                cpu_futures.append(future)

            # Wait for I/O threads to finish
            print("⏳ Stage 1: I/O threads reading files...")
            for t in io_threads:
                t.join()
            print("✅ Stage 1: All files read")

            # Send poison pills to CPU workers
            for _ in range(num_cpu_workers):
                html_queue.put(None)

            # Wait for CPU workers to finish
            print("⏳ Stage 2: CPU workers processing...")
            # The ProcessPoolExecutor context manager will wait for all workers

        print("✅ Stage 2: All HTML parsed and tokenized")

        # Send poison pill to writer
        record_queue.put(None)

        # Wait for writer to finish
        print("⏳ Stage 3: Writer finishing...")
        writer_process.join()
        print("✅ Stage 3: All batches written")

    elapsed_total = time.time() - start_time
    total_records = len(all_html_paths)  # Note: includes duplicates from multiple companies
    avg_rate = total_records / elapsed_total if elapsed_total > 0 else 0

    print(f"\n{'='*50}")
    print(f"3-STAGE PIPELINE COMPLETE")
    print(f"{'='*50}")
    print(f"Total time: {elapsed_total:.1f} seconds")
    print(f"Records processed: {total_records}")
    print(f"Processing rate: {avg_rate:.1f} records/second")
    print(f"Output directory: {output_dir}")

    return total_records


def read_json_folder_batch_optimized(json_files: List[str], df_dict: Optional[Dict], max_content_length: int,
                                    num_processes: int, max_concurrent_io: int, primary_root_path: str,
                                    secondary_root_path: str, max_subdomains_per_company: int = None) -> List[Dict]:
    """Optimized batch processing for all companies - creates pools ONCE for all files

    This function processes all companies in batch mode, creating ThreadPoolExecutor and
    ProcessPoolExecutor only once instead of once per company, resulting in massive performance gains.

    Args:
        json_files: List of JSON file paths
        df_dict: DataFrame dictionary for merging
        max_content_length: Max HTML content length
        num_processes: Number of CPU processes for HTML parsing
        max_concurrent_io: Number of I/O threads for file reading
        primary_root_path: Primary root path for HTML files
        secondary_root_path: Secondary root path for HTML files
        max_subdomains_per_company: Max sub-domains per company

    Returns:
        List of all records from all companies
    """
    total_files = len(json_files)
    print(f"Stage 1/3: Loading {total_files} JSON files...")

    # Step 1: Load all JSON files and collect HTML paths
    all_json_data = []
    all_html_paths = []

    for i, json_file in enumerate(json_files, 1):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            jcn = str(json_data.get('jcn', ''))
            if not jcn:
                continue

            all_json_data.append(json_data)

            # Collect HTML paths from this company
            homepage = json_data.get('homepage', {})

            # Main domain
            main_domain = homepage.get('main_domain', {})
            if main_domain.get('html_path'):
                all_html_paths.append(main_domain['html_path'])

            # Sub-domains (with limit)
            sub_domains = homepage.get('sub_domain', [])
            if max_subdomains_per_company is not None:
                sub_domains = sub_domains[:max_subdomains_per_company]

            for sub_domain in sub_domains:
                if sub_domain.get('html_path'):
                    all_html_paths.append(sub_domain['html_path'])

            if i % 100 == 0:
                print(f"   📝 Loaded {i}/{total_files} JSON files")

        except Exception as e:
            print(f"⚠️ Warning: Could not load {json_file}: {e}")
            continue

    # Remove duplicate paths
    unique_html_paths = list(set(all_html_paths))
    print(f"✅ Loaded {len(all_json_data)} companies with {len(unique_html_paths)} unique HTML files")

    # Step 2: Read ALL HTML files concurrently with ONE ThreadPoolExecutor
    print(f"Stage 2/3: Reading {len(unique_html_paths)} HTML files with {max_concurrent_io} I/O threads...")
    html_contents = {}

    if unique_html_paths:
        with ThreadPoolExecutor(max_workers=max_concurrent_io) as executor:
            futures = {executor.submit(read_file_sync, path, 'utf-8', primary_root_path, secondary_root_path): path
                      for path in unique_html_paths}

            completed = 0
            for future in as_completed(futures):
                path = futures[future]
                try:
                    file_path, content = future.result()
                    html_contents[file_path] = content
                    completed += 1

                    if completed % 500 == 0:
                        print(f"   📝 Read {completed}/{len(unique_html_paths)} HTML files")
                except Exception as e:
                    print(f"⚠️ Warning: Error reading {path}: {e}")
                    html_contents[path] = ""

    print(f"✅ Read {len(html_contents)} HTML files")

    # Step 3: Parse ALL HTML content with ONE ProcessPoolExecutor
    print(f"Stage 3/3: Parsing {len(html_contents)} HTML files with {num_processes or cpu_count()} CPU processes...")
    parsed_contents = {}

    if html_contents:
        if not num_processes:
            num_processes = cpu_count()

        html_tasks = [(path, content, max_content_length) for path, content in html_contents.items() if content]

        with ProcessPoolExecutor(max_workers=num_processes) as executor:
            futures = {executor.submit(parse_html_content_cpu, content, max_length): path
                      for path, content, max_length in html_tasks}

            completed = 0
            for future in as_completed(futures):
                path = futures[future]
                try:
                    parsed_content = future.result()
                    parsed_contents[path] = parsed_content
                    completed += 1

                    if completed % 500 == 0:
                        print(f"   📝 Parsed {completed}/{len(html_tasks)} HTML files")
                except Exception as e:
                    print(f"⚠️ Warning: Error parsing HTML for {path}: {e}")
                    parsed_contents[path] = ""

    print(f"✅ Parsed {len(parsed_contents)} HTML files")

    # Step 4: Build final records using pre-processed content
    print(f"Building records for {len(all_json_data)} companies...")
    all_records = []

    for i, json_data in enumerate(all_json_data, 1):
        company_records = build_company_records(json_data, df_dict, parsed_contents, max_subdomains_per_company)
        all_records.extend(company_records)

        if i % 100 == 0:
            print(f"   📝 Built records for {i}/{len(all_json_data)} companies")

    print(f"✅ Successfully loaded {len(all_records)} records from {len(all_json_data)} companies")
    return all_records


def read_json_folder(json_folder: str, dataframe_file: Optional[str] = None, max_content_length: int = 10000,
                    extra_columns: Optional[List[str]] = None, use_hybrid_pipeline: bool = False,
                    num_processes: int = None, max_concurrent_io: int = 20, primary_root_path: str = '', secondary_root_path: str = '',
                    max_subdomains_per_company: int = None) -> List[Dict]:
    """Read JSON files from folder and optionally merge with DataFrame
    
    Args:
        json_folder: Path to folder containing JSON files
        dataframe_file: Path to CSV file with additional company information
        max_content_length: Maximum HTML content length for tokenization
        extra_columns: List of specific columns to merge from DataFrame (if None, uses all columns)
    """
    print(f"Reading JSON files from folder: {json_folder}")
    
    if not os.path.exists(json_folder):
        print(f"❌ Error: JSON folder does not exist: {json_folder}")
        return []
    
    # Find all JSON files in the folder
    json_files = glob.glob(os.path.join(json_folder, "*.json"))
    if not json_files:
        print(f"❌ Error: No JSON files found in {json_folder}")
        return []
    
    print(f"Found {len(json_files)} JSON files")
    
    # Load DataFrame if provided and convert to dictionary for fast lookup
    df_dict = None
    if dataframe_file:
        try:
            # Determine which columns to read
            if extra_columns:
                # Read only DOMESTIC_DESCRIMI_NO + extra_columns for better performance
                columns_to_read = ['DOMESTIC_DESCRIMI_NO'] + extra_columns
                df_data = pd.read_csv(dataframe_file, usecols=lambda x: x in columns_to_read, encoding="cp932")
                
                # Check which columns were actually found
                available_columns = ['DOMESTIC_DESCRIMI_NO'] + [col for col in extra_columns if col in df_data.columns and col != 'DOMESTIC_DESCRIMI_NO']
                missing_columns = [col for col in extra_columns if col not in df_data.columns]
                
                if missing_columns:
                    print(f"⚠️  Warning: Columns not found in DataFrame: {missing_columns}")
                
                print(f"Using specific columns: {available_columns[1:]} (+ DOMESTIC_DESCRIMI_NO as key)")
            else:
                # Read all columns if no specific columns requested
                df_data = pd.read_csv(dataframe_file)
                print(f"Using all DataFrame columns ({len(df_data.columns)} columns)")
            
            # Clean the data
            df_data = df_data[df_data['DOMESTIC_DESCRIMI_NO'].notnull()]
            df_data.drop_duplicates(subset=['DOMESTIC_DESCRIMI_NO'], inplace=True)
            
            # Convert to dictionary with jcn as key for O(1) lookup
            df_data['DOMESTIC_DESCRIMI_NO'] = df_data['DOMESTIC_DESCRIMI_NO'].apply(lambda x: str(int(float(x))))
            df_dict = df_data.set_index('DOMESTIC_DESCRIMI_NO').to_dict('index')
            print(f"Loaded DataFrame with {len(df_data)} records from {dataframe_file}")
            print(f"Created lookup dictionary with {len(df_dict)} DOMESTIC_DESCRIMI_NO keys")
        except Exception as e:
            print(f"⚠️  Warning: Could not load DataFrame: {e}")
            df_dict = None

    # Use hybrid pipeline with streaming (creates pools once for all companies)
    if use_hybrid_pipeline:
        print("Using hybrid pipeline with streaming (optimized)...")
        return read_json_folder_streaming(json_files, df_dict, max_content_length, num_processes,
                                         max_concurrent_io, primary_root_path, secondary_root_path,
                                         max_subdomains_per_company)

    # Sequential processing (fallback for non-hybrid mode)
    records = []
    total_files = len(json_files)

    for i, json_file in enumerate(json_files, 1):
        try:
            with open(json_file, 'r', encoding='utf-8') as f:
                json_data = json.load(f)

            # Convert JSON structure to URL-based records (one per URL)
            url_records = convert_json_to_records(json_data, df_dict, max_content_length, max_subdomains_per_company)
            records.extend(url_records)

            if i % 100 == 0:
                print(f"   📝 Processed {i}/{total_files} JSON files")

        except Exception as e:
            print(f"⚠️ Warning: Could not process {json_file}: {e}")
            continue

    print(f"✅ Successfully loaded {len(records)} records from JSON files")
    return records


def extract_text_from_html(html_path: str, max_length: int = 10000) -> str:
    """Extract text content from HTML file"""
    try:
        if not html_path or not os.path.exists(html_path):
            return ""
        
        with open(html_path, 'r', encoding='utf-8') as f:
            html_content = f.read()
        
        # Parse HTML and extract text
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it up
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Truncate if too long
        text = text[:max_length]
        
        return text
        
    except Exception as e:
        print(f"⚠️ Warning: Could not extract text from {html_path}: {e}")
        return ""


def extract_html_content_mp(html_task: Tuple[str, int]) -> str:
    """Multiprocessing-compatible function to extract HTML content"""
    html_path, max_length = html_task
    return extract_text_from_html(html_path, max_length)


def read_file_sync(file_path: str, encoding: str = 'utf-8', primary_root_path: str = '', secondary_root_path: str = '') -> Tuple[str, str]:
    """Synchronously read a file for ThreadPoolExecutor with configurable root paths"""
    try:
        if not file_path:
            return file_path, ""

        # Try primary_root_path + file_path first
        if primary_root_path:
            full_path = primary_root_path + file_path
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding=encoding) as f:
                    content = f.read()
                return file_path, content

        # Try secondary_root_path + file_path if primary failed
        if secondary_root_path:
            full_path = secondary_root_path + file_path
            if os.path.exists(full_path):
                with open(full_path, 'r', encoding=encoding) as f:
                    content = f.read()
                return file_path, content

        # Try file_path as-is (absolute path)
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
            return file_path, content

        return file_path, ""
    except Exception as e:
        print(f"⚠️ Warning: Could not read {file_path}: {e}")
        return file_path, ""


def read_files_concurrently(file_paths: List[str], max_concurrent: int = 20, primary_root_path: str = '', secondary_root_path: str = '') -> Dict[str, str]:
    """Read multiple files concurrently using ThreadPoolExecutor with configurable root paths"""
    results = {}

    if not file_paths:
        return results

    # Use ThreadPoolExecutor for concurrent I/O
    with ThreadPoolExecutor(max_workers=min(max_concurrent, len(file_paths))) as executor:
        # Submit all file reading tasks
        futures = {executor.submit(read_file_sync, path, 'utf-8', primary_root_path, secondary_root_path): path for path in file_paths}

        # Collect results as they complete
        for future in as_completed(futures):
            try:
                file_path, content = future.result()
                results[file_path] = content
            except Exception as e:
                path = futures[future]
                print(f"⚠️ Warning: Error reading {path}: {e}")
                results[path] = ""

    return results


def parse_html_content_cpu(html_content: str, max_length: int = 10000) -> str:
    """CPU-intensive HTML parsing (for ProcessPoolExecutor)"""
    try:
        if not html_content:
            return ""
        
        # Parse HTML and extract text
        soup = BeautifulSoup(html_content, 'lxml')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
        
        # Get text and clean it up
        text = soup.get_text()
        
        # Clean up whitespace
        lines = (line.strip() for line in text.splitlines())
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        text = ' '.join(chunk for chunk in chunks if chunk)
        
        # Truncate if too long
        text = text[:max_length]
        
        return text
        
    except Exception as e:
        print(f"⚠️ Warning: Could not parse HTML content: {e}")
        return ""


def process_html_batch_cpu(html_batch: List[Tuple[str, str, int]]) -> List[Tuple[str, str]]:
    """Process a batch of HTML content in parallel (for ProcessPoolExecutor)"""
    results = []
    for file_path, html_content, max_length in html_batch:
        parsed_content = parse_html_content_cpu(html_content, max_length)
        results.append((file_path, parsed_content))
    return results


def convert_json_to_records_hybrid(json_data: Dict, df_dict: Optional[Dict] = None,
                                  max_content_length: int = 10000, num_processes: int = None,
                                  max_concurrent_io: int = 20, primary_root_path: str = '', secondary_root_path: str = '',
                                  max_subdomains_per_company: int = None) -> List[Dict]:
    """Convert JSON structure to multiple URL-based records using hybrid I/O + CPU processing"""
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
            'main_domain_url': json_data.get('homepage', {}).get('main_domain', {}).get('url', ''),
        }
        
        # Merge with DataFrame dictionary if provided (O(1) lookup)
        if df_dict is not None and jcn in df_dict:
            df_record = df_dict[jcn]
            # Merge additional fields from DataFrame
            for col, value in df_record.items():
                if col not in base_info and pd.notna(value):
                    base_info[col] = value
        
        homepage = json_data.get('homepage', {})
        
        # Collect all HTML file paths for concurrent I/O
        html_paths = []
        domain_info = []
        
        # Main domain
        main_domain = homepage.get('main_domain', {})
        if main_domain.get('url'):
            html_path = main_domain.get('html_path', '')
            if html_path:
                html_paths.append(html_path)
            domain_info.append({
                'type': 'main',
                'url': main_domain['url'],
                'html_path': html_path,
                'tags': [],
                'index': 0
            })
        
        # Sub-domains (limit if max_subdomains_per_company is set)
        sub_domains = homepage.get('sub_domain', [])
        if max_subdomains_per_company is not None:
            sub_domains = sub_domains[:max_subdomains_per_company]

        for i, sub_domain in enumerate(sub_domains):
            if sub_domain.get('url'):
                html_path = sub_domain.get('html_path', '')
                if html_path:
                    html_paths.append(html_path)
                domain_info.append({
                    'type': 'sub',
                    'url': sub_domain['url'],
                    'html_path': html_path,
                    'tags': sub_domain.get('tags', []),
                    'index': i + 1
                })
        
        # Stage 1: Concurrent I/O - Read all HTML files at once
        html_contents = {}
        if html_paths:
            html_contents = read_files_concurrently(html_paths, max_concurrent_io, primary_root_path, secondary_root_path)
        
        # Stage 2: CPU-intensive processing - Parse HTML in parallel
        parsed_contents = {}
        if html_contents:
            # Prepare tasks for ProcessPoolExecutor
            html_tasks = [(path, content, max_content_length) 
                         for path, content in html_contents.items()]
            
            # Use ProcessPoolExecutor for CPU-intensive HTML parsing
            if not num_processes:
                num_processes = min(len(html_tasks), cpu_count())
                
            with ProcessPoolExecutor(max_workers=num_processes) as executor:
                # Submit batch processing tasks
                batch_size = max(1, len(html_tasks) // num_processes)
                futures = []
                
                for i in range(0, len(html_tasks), batch_size):
                    batch = html_tasks[i:i + batch_size]
                    future = executor.submit(process_html_batch_cpu, batch)
                    futures.append(future)
                
                # Collect results
                for future in as_completed(futures):
                    batch_results = future.result()
                    for file_path, parsed_content in batch_results:
                        parsed_contents[file_path] = parsed_content
        
        # Stage 3: Build final records with processed content
        records = []
        for domain in domain_info:
            record = base_info.copy()
            
            # Get processed HTML content or fallback
            html_content = ""
            if domain['html_path'] and domain['html_path'] in parsed_contents:
                html_content = parsed_contents[domain['html_path']]
            
            # Build content parts
            content_parts = [base_info['company_name_kj']]
            
            if html_content:
                content_parts.append(html_content)
            elif domain['type'] == 'main':
                # Fallback to URL for main domain
                content_parts.append(domain['url'])
            else:
                # Fallback to tags for sub-domains
                content_parts.extend(domain['tags'])
            
            # Create record based on domain type
            if domain['type'] == 'main':
                record.update({
                    'id': f"{jcn}_main",
                    'url': domain['url'],
                    'url_name': 'メインサイト',
                    'content': ' '.join(filter(None, content_parts))
                })
            else:
                record.update({
                    'id': f"{jcn}_sub_{domain['index']}",
                    'url': domain['url'],
                    'url_name': ' '.join(domain['tags']) if domain['tags'] else f"サブページ{domain['index']}",
                    'content': ' '.join(filter(None, content_parts))
                })
            
            records.append(record)
        
        return records
        
    except Exception as e:
        print(f"⚠️  Warning: Error converting JSON record: {e}")
        return []


def convert_json_to_records(json_data: Dict, df_dict: Optional[Dict] = None, max_content_length: int = 10000,
                           max_subdomains_per_company: int = None) -> List[Dict]:
    """Backward compatibility wrapper - uses sequential processing"""
    # Use original sequential processing for backward compatibility
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
            
            # Extract content from HTML if available
            html_path = main_domain.get('html_path', '')
            html_content = extract_text_from_html(html_path, max_content_length) if html_path else ""
            
            # Combine company name with HTML content
            content_parts = [base_info['company_name_kj']]
            if html_content:
                content_parts.append(html_content)
            else:
                # Fallback to URL if no HTML content
                content_parts.append(main_domain['url'])
            
            main_record.update({
                'id': f"{jcn}_main",
                'url': main_domain['url'],
                'url_name': 'メインサイト',
                'content': ' '.join(filter(None, content_parts))
            })
            records.append(main_record)
        
        # Create records for each sub-domain (limit if max_subdomains_per_company is set)
        sub_domains = homepage.get('sub_domain', [])
        if max_subdomains_per_company is not None:
            sub_domains = sub_domains[:max_subdomains_per_company]

        for i, sub_domain in enumerate(sub_domains):
            if sub_domain.get('url'):
                sub_record = base_info.copy()
                
                # Extract content from HTML if available
                html_path = sub_domain.get('html_path', '')
                html_content = extract_text_from_html(html_path, max_content_length) if html_path else ""
                
                # Build content from HTML or tags
                tags = sub_domain.get('tags', [])
                content_parts = [base_info['company_name_kj']]
                
                if html_content:
                    # Use HTML content if available
                    content_parts.append(html_content)
                else:
                    # Fallback to tags if no HTML content
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


# Global variable for process-local tokenizer (used in multiprocessing)
_process_tokenizer = None


def init_tokenizer_worker(tokenizer_type: Optional[str]):
    """Initialize tokenizer once per worker process"""
    global _process_tokenizer
    _process_tokenizer = JapaneseTokenizer(tokenizer_type)


def tokenize_record_mp(record: Dict) -> Dict:
    """Multiprocessing-compatible function to tokenize a single record using pre-initialized tokenizer"""
    # Tokenize the content field using the pre-initialized tokenizer
    content_analysis = _process_tokenizer.tokenize_text(record.get('content', ''))

    # Create tokenized record
    tokenized_record = record.copy()  # Keep all original fields

    # Add tokenization results
    tokenized_record['content_tokens'] = content_analysis['content_tokens']
    tokenized_record['token_count'] = content_analysis['token_count']

    # Remove original content to save space (keeping only tokenized version)
    if 'content' in tokenized_record:
        del tokenized_record['content']

    return tokenized_record


def process_batch_tokenization(tokenizer: JapaneseTokenizer, batch: List[Dict], batch_num: int) -> List[Dict]:
    """Process a batch of records and tokenize content (single-threaded)"""
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


def process_batch_tokenization_mp(batch: List[Dict], batch_num: int, num_processes: int = None, tokenizer_type: Optional[str] = None) -> List[Dict]:
    """Process a batch of records using multiprocessing with pre-initialized tokenizers"""
    if not num_processes:
        num_processes = cpu_count()

    print(f"🔄 Tokenizing batch {batch_num} ({len(batch)} records) using {num_processes} processes...")

    start_time = time.time()

    # Calculate optimal chunksize for better load distribution
    chunksize = max(1, len(batch) // (num_processes * 4))

    # Use multiprocessing pool with initializer to create tokenizer once per process
    with Pool(processes=num_processes, initializer=init_tokenizer_worker, initargs=(tokenizer_type,)) as pool:
        tokenized_records = pool.map(tokenize_record_mp, batch, chunksize=chunksize)

    elapsed = time.time() - start_time
    print(f"✅ Batch {batch_num} tokenized in {elapsed:.2f} seconds with multiprocessing")

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


def create_processing_summary(output_dir: str, total_batches: int, total_records: int, processing_time: float,
                             use_multiprocessing: bool = False, num_processes: int = None, tokenizer_type: Optional[str] = None) -> str:
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
            'tokenizer': tokenizer_type if tokenizer_type else 'auto-detect',
            'multiprocessing_enabled': use_multiprocessing,
            'num_processes': num_processes if use_multiprocessing else 1
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
    """Generate output directory using new organized structure: data/tokenized/{prefecture}"""
    if output_dir:
        return output_dir

    if json_folder:
        # Extract prefecture from path like "data/raw/tokyo"
        prefecture = os.path.basename(json_folder.rstrip('/'))
        return f"data/tokenized/{prefecture}"
    elif csv_file:
        csv_name = os.path.splitext(os.path.basename(csv_file))[0]
        return f"data/tokenized/{csv_name}"
    else:
        return "data/tokenized"


# Add the parent directory to the path to import app modules
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, PROJECT_ROOT)

from app.services.tokenizers import get_tokenizer

@hydra.main(version_base=None, config_path="../conf", config_name="tokenize")
def main(cfg: DictConfig) -> None:
    """Main function with Hydra configuration"""
    
    # Extract configuration values
    csv_file = cfg.input.csv_file
    json_folder = cfg.input.json_folder
    dataframe_file = cfg.input.dataframe_file
    batch_size = cfg.processing.batch_size
    max_content_length = cfg.processing.max_content_length
    extra_columns = cfg.processing.extra_columns
    use_multiprocessing = cfg.processing.use_multiprocessing
    num_processes = cfg.processing.num_processes
    use_hybrid_pipeline = cfg.processing.get('use_hybrid_pipeline', False)
    use_streaming_pipeline = cfg.processing.get('use_streaming_pipeline', False)
    max_concurrent_io = cfg.processing.get('max_concurrent_io', 20)
    num_cpu_workers = cfg.processing.get('num_cpu_workers', None)
    max_subdomains_per_company = cfg.processing.get('max_subdomains_per_company', None)
    tokenizer_type = cfg.tokenizer.get('type', None) if 'tokenizer' in cfg else None
    primary_root_path = cfg.input.get('primary_root_path', '')
    secondary_root_path = cfg.input.get('secondary_root_path', '')
    output_dir = cfg.output.output_dir
    clear_output = cfg.output.clear_output
    
    # Validate configuration
    if csv_file and not os.path.exists(csv_file):
        print(f"❌ Error: CSV file does not exist: {csv_file}")
        sys.exit(1)
        
    if json_folder and not os.path.exists(json_folder):
        print(f"❌ Error: JSON folder does not exist: {json_folder}")
        sys.exit(1)
        
    if dataframe_file and not os.path.exists(dataframe_file):
        print(f"❌ Error: DataFrame file does not exist: {dataframe_file}")
        sys.exit(1)
        
    if dataframe_file and not json_folder:
        print("❌ Error: dataframe_file can only be used with json_folder")
        sys.exit(1)
    
    if batch_size <= 0:
        print("❌ Error: Batch size must be a positive integer")
        sys.exit(1)
        
    if not csv_file and not json_folder:
        print("❌ Error: Either csv_file or json_folder must be specified")
        sys.exit(1)
    
    # Determine output directory
    if not output_dir:
        output_dir = get_output_dir(csv_file, json_folder, None)
    
    print("EOS Tokenization Script")
    print("=" * 50)
    if csv_file:
        print(f"Input: CSV File - {csv_file}")
    else:
        print(f"Input: JSON Folder - {json_folder}")
        if dataframe_file:
            print(f"DataFrame: {dataframe_file}")
    print(f"Batch Size: {batch_size}")
    print(f"Output Directory: {output_dir}")

    if use_streaming_pipeline and json_folder:
        actual_cpu_workers = num_cpu_workers if num_cpu_workers else cpu_count()
        print(f"3-Stage Streaming Pipeline: Enabled")
        print(f"  - I/O workers: {max_concurrent_io}")
        print(f"  - CPU workers: {actual_cpu_workers}")
        print(f"  - Writer: 1 process")
    else:
        print(f"Multiprocessing: {'Enabled' if use_multiprocessing else 'Disabled'}")
        if use_multiprocessing:
            actual_processes = num_processes if num_processes else cpu_count()
            print(f"Processes: {actual_processes}")
        if use_hybrid_pipeline:
            print(f"Hybrid Pipeline: Enabled (I/O workers: {max_concurrent_io})")
    print()
    
    # Setup output directory
    if clear_output and os.path.exists(output_dir):
        import shutil
        print(f"Clearing output directory: {output_dir}")
        shutil.rmtree(output_dir)
    
    if not os.path.exists(output_dir):
        os.makedirs(output_dir, exist_ok=True)
        print(f"Created output directory: {output_dir}")
    
    # Initialize tokenizer
    print("Initializing Japanese tokenizer...")
    tokenizer = JapaneseTokenizer(tokenizer_type)
    if tokenizer_type:
        print(f"✅ Tokenizer ready (using {tokenizer_type})")
    else:
        print("✅ Tokenizer ready (using auto-detect)")
    print()
    
    # Read input data
    start_time = time.time()
    if csv_file:
        # Read CSV file in batches
        batches = read_csv_batch(csv_file, batch_size)
        input_type = "CSV"
        total_records = sum(len(batch) for batch in batches)
    elif use_streaming_pipeline and json_folder:
        # Use 3-stage streaming pipeline (tokenization happens in pipeline)
        print("Using 3-stage streaming pipeline (I/O → CPU+Tokenize → Writer)...")
        print()

        # Get JSON files
        json_files = glob.glob(os.path.join(json_folder, '*.json'))

        # Load DataFrame if specified
        df_dict = None
        if dataframe_file:
            try:
                df = pd.read_csv(dataframe_file, encoding='utf-8', dtype=str)
                df_dict = {str(row.get('jcn', '')): row.to_dict() for _, row in df.iterrows() if row.get('jcn')}
                print(f"✅ Loaded DataFrame with {len(df_dict)} records")
            except Exception as e:
                print(f"⚠️  Warning: Could not load DataFrame: {e}")
                df_dict = None

        # Prepare tokenizer config
        tokenizer_config = {
            'type': tokenizer_type,
            'included_pos': cfg.tokenizer.get('included_pos', []),
            'min_word_length': cfg.tokenizer.get('min_word_length', 2),
            'stop_words_filtered': cfg.tokenizer.get('stop_words_filtered', True)
        }

        # Run 3-stage pipeline (writes files directly, no batches returned)
        total_records = read_json_folder_3stage_pipeline(
            json_files, df_dict, max_content_length,
            num_cpu_workers, max_concurrent_io,
            primary_root_path, secondary_root_path,
            max_subdomains_per_company,
            tokenizer_config, output_dir, batch_size
        )

        # 3-stage pipeline already wrote files and created summary
        elapsed_total = time.time() - start_time

        # Create summary file
        num_batches = (total_records + batch_size - 1) // batch_size  # Ceiling division
        create_processing_summary(output_dir, num_batches, total_records, elapsed_total,
                                True, num_cpu_workers, tokenizer_type)

        # Print completion message
        records_per_second = total_records / elapsed_total if elapsed_total > 0 else 0
        print(f"\nProcessing rate: {records_per_second:.1f} records/second")
        print("\n✅ Next steps:")
        print(f"   python scripts/create_index.py --tokenized-dir {output_dir}")
        print(f"   # Tokenized from JSON folder: {json_folder}")
        if dataframe_file:
            print(f"   # Merged with DataFrame: {dataframe_file}")

        # Exit early since 3-stage pipeline already completed everything
        sys.exit(0)
    else:
        # Read JSON folder and create batches (traditional approach)
        records = read_json_folder(json_folder, dataframe_file, max_content_length, extra_columns,
                                 use_hybrid_pipeline, num_processes, max_concurrent_io, primary_root_path,
                                 secondary_root_path, max_subdomains_per_company)
        if not records:
            print("❌ No data to process. Exiting.")
            sys.exit(1)

        # Create batches from records
        batches = []
        for i in range(0, len(records), batch_size):
            batch = records[i:i + batch_size]
            batches.append(batch)
        input_type = "JSON"
        total_records = sum(len(batch) for batch in batches)

    if not batches:
        print(f"❌ No {input_type.lower()} data to process. Exiting.")
        sys.exit(1)
    
    print(f"Starting tokenization...")
    print(f"Total records: {total_records}")
    print(f"Total batches: {len(batches)}")
    print(f"Input type: {input_type}")
    print()
    
    # Process each batch
    successful_batches = 0
    for i, batch in enumerate(batches, 1):
        # Tokenize batch using multiprocessing or single-threaded approach
        if use_multiprocessing:
            tokenized_records = process_batch_tokenization_mp(batch, i, num_processes, tokenizer_type)
        else:
            tokenized_records = process_batch_tokenization(tokenizer, batch, i)
        
        if tokenized_records:
            # Save tokenized batch
            saved_file = save_tokenized_batch(tokenized_records, output_dir, i)
            if saved_file:
                successful_batches += 1
        
        # Show progress
        progress = (i / len(batches)) * 100
        print(f"Progress: {progress:.1f}% ({i}/{len(batches)} batches)")
        print()
    
    # Final statistics
    elapsed_total = time.time() - start_time
    
    print("=" * 50)
    print("TOKENIZATION COMPLETE")
    print("=" * 50)
    print(f"Total time: {elapsed_total:.2f} seconds")
    print(f"✅ Successful batches: {successful_batches}/{len(batches)}")
    print(f"Records processed: {total_records}")
    print(f"Output directory: {output_dir}")
    
    # Create summary file
    create_processing_summary(output_dir, len(batches), total_records, elapsed_total, use_multiprocessing, num_processes, tokenizer_type)
    
    if successful_batches == len(batches):
        print("✅ Tokenization completed successfully!")
        print()
        print("Next steps:")
        if csv_file:
            print(f"   python scripts/create_index.py --tokenized-dir {output_dir}")
        else:
            print(f"   python scripts/create_index.py --tokenized-dir {output_dir}")
            print(f"   # Tokenized from JSON folder: {json_folder}")
            if dataframe_file:
                print(f"   # Merged with DataFrame: {dataframe_file}")
    else:
        failed_batches = len(batches) - successful_batches
        print(f"⚠️ Tokenization completed with {failed_batches} failed batches")
    
    # Performance metrics
    if total_records > 0:
        records_per_second = total_records / elapsed_total
        print(f"Processing rate: {records_per_second:.1f} records/second")


if __name__ == '__main__':
    main()