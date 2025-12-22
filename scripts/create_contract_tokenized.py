#!/usr/bin/env python3
"""
Create Contract Tokenized Data

Reads tokenized data from data/tokenized/, filters for contract records (CUST_STATUS2="契約"),
enriches with producer/district information, and writes to district-based structure.

Usage:
    python scripts/create_contract_tokenized.py
"""

import os
import json
import pandas as pd
import yaml
from collections import defaultdict
from typing import Dict, List
import glob

# District code mapping (must match convert_contract_data_to_json.py)
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


def load_config():
    """Load configuration from json_companies.yaml"""
    config_path = "conf/json_companies.yaml"

    if not os.path.exists(config_path):
        raise FileNotFoundError(f"Config file not found: {config_path}")

    with open(config_path, 'r', encoding='utf-8') as f:
        config = yaml.safe_load(f)

    return config


def load_producer_lookup(config: Dict) -> Dict[str, Dict]:
    """
    Load and join dataframe with t_producer to create lookup table

    Returns:
        Dict mapping DOMESTIC_DESCRIMI_NO to producer info (5 fields)
    """
    print("Loading producer lookup data...")

    # Load dataframe file (only needed columns)
    dataframe_file = config['input']['dataframe_file']
    if not os.path.exists(dataframe_file):
        raise FileNotFoundError(f"Dataframe file not found: {dataframe_file}")

    print(f"  Reading dataframe: {dataframe_file}")
    df = pd.read_csv(dataframe_file, encoding='cp932', usecols=['DOMESTIC_DESCRIMI_NO', 'PRODUCER_CD'])

    # Clean the data
    df = df[df['DOMESTIC_DESCRIMI_NO'].notnull()]
    df.drop_duplicates(subset=['DOMESTIC_DESCRIMI_NO'], inplace=True)

    # Convert DOMESTIC_DESCRIMI_NO to string (same as tokenize_csv_streaming.py)
    df['DOMESTIC_DESCRIMI_NO'] = df['DOMESTIC_DESCRIMI_NO'].apply(lambda x: str(int(float(x))))

    print(f"    Loaded {len(df)} records (after cleaning)")

    # Load t_producer file
    t_producer_file = config['input']['t_producer_file']
    if not os.path.exists(t_producer_file):
        raise FileNotFoundError(f"t_producer file not found: {t_producer_file}")

    print(f"  Reading t_producer: {t_producer_file}")
    t_producer = pd.read_csv(t_producer_file, usecols=[
        'PRODUCER_CD_ML',
        'DISTRICT_NAME',
        'MOTHERBRANCH_CD',
        'BRANCH_NAME',
        'SOLICITOR_CD',
        'SOLICITOR'
    ])
    print(f"    Loaded {len(t_producer)} records")

    # Join: df.PRODUCER_CD = t_producer.PRODUCER_CD_ML
    print("  Joining dataframe with t_producer...")
    joined = df.merge(
        t_producer,
        left_on='PRODUCER_CD',
        right_on='PRODUCER_CD_ML',
        how='inner'  # Inner join - drop unmatched
    )
    print(f"    Joined result: {len(joined)} records (dropped {len(df) - len(joined)} unmatched)")

    # Create lookup dictionary: DOMESTIC_DESCRIMI_NO -> producer info
    lookup = {}
    for _, row in joined.iterrows():
        lookup[row['DOMESTIC_DESCRIMI_NO']] = {
            'DISTRICT_NAME': row['DISTRICT_NAME'],
            'MOTHERBRANCH_CD': row['MOTHERBRANCH_CD'],
            'BRANCH_NAME': row['BRANCH_NAME'],
            'SOLICITOR_CD': row['SOLICITOR_CD'],
            'SOLICITOR': row['SOLICITOR']
        }

    print(f"  Created lookup table with {len(lookup)} unique companies")

    # Show district distribution
    district_counts = defaultdict(int)
    for info in lookup.values():
        district_name = info.get('DISTRICT_NAME', 'Unknown')
        district_counts[district_name] += 1

    print("\n  District distribution:")
    for district_name in sorted(district_counts.keys()):
        district_code = DISTRICT_MAPPING.get(district_name, '?')
        count = district_counts[district_name]
        print(f"    {district_code} ({district_name}): {count} companies")

    return lookup


class DistrictBatchWriter:
    """Streaming batch writer for district-based output"""

    def __init__(self, output_base_dir: str, batch_size: int):
        self.output_base_dir = output_base_dir
        self.batch_size = batch_size

        # Buffers: district_code -> list of records
        self.buffers = defaultdict(list)

        # Batch counters: district_code -> current batch number
        self.batch_numbers = defaultdict(int)

        # Statistics
        self.total_written = defaultdict(int)

        # Create output directory
        os.makedirs(output_base_dir, exist_ok=True)

    def add_record(self, district_code: str, record: Dict):
        """Add a record to district buffer, flush if full"""
        self.buffers[district_code].append(record)

        # Flush if buffer is full
        if len(self.buffers[district_code]) >= self.batch_size:
            self._flush_buffer(district_code)

    def _flush_buffer(self, district_code: str):
        """Write buffer to disk and clear"""
        if not self.buffers[district_code]:
            return

        # Create district directory
        district_dir = os.path.join(self.output_base_dir, district_code)
        os.makedirs(district_dir, exist_ok=True)

        # Write batch file
        batch_num = self.batch_numbers[district_code]
        batch_file = os.path.join(district_dir, f"batch_{batch_num}.json")

        with open(batch_file, 'w', encoding='utf-8') as f:
            json.dump(self.buffers[district_code], f, ensure_ascii=False, indent=2)

        num_records = len(self.buffers[district_code])
        self.total_written[district_code] += num_records

        print(f"  💾 Wrote {district_code}/batch_{batch_num}.json: {num_records} records")

        # Clear buffer and increment counter
        self.buffers[district_code] = []
        self.batch_numbers[district_code] += 1

    def flush_all(self):
        """Flush all remaining buffers"""
        print("\nFlushing remaining buffers...")
        for district_code in list(self.buffers.keys()):
            if self.buffers[district_code]:
                self._flush_buffer(district_code)

    def print_summary(self):
        """Print writing summary"""
        print("\n" + "="*60)
        print("📊 Writing Summary")
        print("="*60)

        total = 0
        for district_code in sorted(self.total_written.keys()):
            count = self.total_written[district_code]
            batches = self.batch_numbers[district_code]
            total += count
            print(f"  {district_code}: {count} records in {batches} batches")

        print(f"\n  Total: {total} records across {len(self.total_written)} districts")
        print("="*60)


def process_tokenized_data(lookup: Dict[str, Dict], batch_size: int,
                          input_dir: str = "data/tokenized",
                          output_dir: str = "data/tokenized_contract"):
    """
    Process tokenized data with streaming approach

    Args:
        lookup: DOMESTIC_DESCRIMI_NO -> producer info mapping
        batch_size: Records per batch file
        input_dir: Input directory with tokenized batches
        output_dir: Output directory for contract batches
    """
    print(f"\n{'='*60}")
    print("Processing Tokenized Data (Streaming)")
    print(f"{'='*60}")
    print(f"Input: {input_dir}")
    print(f"Output: {output_dir}")
    print(f"Batch size: {batch_size}")
    print()

    # Initialize batch writer
    writer = DistrictBatchWriter(output_dir, batch_size)

    # Find all batch files in prefecture subfolders
    # Pattern: data/tokenized/{prefecture}/batch_*.json or tokenized_batch_*.json
    batch_files = []
    batch_files.extend(sorted(glob.glob(os.path.join(input_dir, "*", "batch_*.json"))))
    batch_files.extend(sorted(glob.glob(os.path.join(input_dir, "*", "tokenized_batch_*.json"))))

    # Remove duplicates, filter out summary files, and sort
    batch_files = [f for f in set(batch_files) if 'summary' not in os.path.basename(f).lower()]
    batch_files = sorted(batch_files)

    if not batch_files:
        print(f"⚠️  No batch files found in {input_dir}")
        print(f"    Looking for: {input_dir}/{{prefecture}}/batch_*.json")
        print(f"    Or: {input_dir}/{{prefecture}}/tokenized_batch_*.json")
        return

    print(f"Found {len(batch_files)} batch files across prefecture subfolders\n")

    # Statistics
    total_input_records = 0
    total_contract_records = 0
    total_enriched_records = 0
    total_dropped_records = 0

    # Track unmatched DOMESTIC_DESCRIMI_NO for debugging
    unmatched_samples = set()

    # Process each batch file
    for i, batch_file in enumerate(batch_files, 1):
        batch_name = os.path.basename(batch_file)
        print(f"Processing batch {i}/{len(batch_files)}: {batch_name}")

        with open(batch_file, 'r', encoding='utf-8') as f:
            records = json.load(f)

        total_input_records += len(records)

        batch_contract = 0
        batch_enriched = 0
        batch_dropped = 0

        for record in records:
            # Filter: only 契約 records
            if record.get('CUST_STATUS2') != '契約':
                continue

            batch_contract += 1

            # Lookup producer info
            # Ensure DOMESTIC_DESCRIMI_NO is in correct format (same as dataframe conversion)
            domestic_no = record.get('DOMESTIC_DESCRIMI_NO')
            if not domestic_no:
                batch_dropped += 1
                continue

            # Convert to string format to match lookup table
            try:
                domestic_no = str(int(float(domestic_no)))
            except (ValueError, TypeError):
                # If conversion fails, try as-is
                pass

            if domestic_no not in lookup:
                batch_dropped += 1
                # Collect sample unmatched values for debugging (limit to 10)
                if len(unmatched_samples) < 10:
                    unmatched_samples.add(domestic_no)
                continue

            # Enrich record with producer info
            producer_info = lookup[domestic_no]
            record.update(producer_info)

            batch_enriched += 1

            # Add to appropriate district buffer
            district_name = producer_info['DISTRICT_NAME']
            district_code = DISTRICT_MAPPING.get(district_name)

            if not district_code:
                print(f"    ⚠️  Unknown district: {district_name}")
                batch_dropped += 1
                continue

            writer.add_record(district_code, record)

        total_contract_records += batch_contract
        total_enriched_records += batch_enriched
        total_dropped_records += batch_dropped

        print(f"    契約 records: {batch_contract}, Enriched: {batch_enriched}, Dropped: {batch_dropped}")

    # Flush remaining buffers
    writer.flush_all()

    # Print summary
    print("\n" + "="*60)
    print("📊 Processing Summary")
    print("="*60)
    print(f"Total input records: {total_input_records:,}")
    print(f"Contract records (CUST_STATUS2='契約'): {total_contract_records:,}")
    print(f"Successfully enriched: {total_enriched_records:,}")
    print(f"Dropped (no producer match): {total_dropped_records:,}")

    # Show debugging info for unmatched records
    if unmatched_samples:
        print(f"\n🔍 Sample unmatched DOMESTIC_DESCRIMI_NO values (first 10):")
        for sample in sorted(list(unmatched_samples)[:10]):
            print(f"    '{sample}' (type: {type(sample).__name__})")

        # Show sample lookup keys for comparison
        sample_lookup_keys = list(lookup.keys())[:5]
        print(f"\n🔍 Sample lookup table keys (first 5):")
        for key in sample_lookup_keys:
            print(f"    '{key}' (type: {type(key).__name__})")

    print()

    writer.print_summary()


def main():
    """Main execution"""
    print("="*60)
    print("Create Contract Tokenized Data")
    print("="*60)
    print()

    # Load configuration
    config = load_config()
    batch_size = config['processing']['batch_size']

    print(f"Configuration loaded:")
    print(f"  Dataframe file: {config['input']['dataframe_file']}")
    print(f"  t_producer file: {config['input']['t_producer_file']}")
    print(f"  Batch size: {batch_size}")
    print()

    # Load producer lookup table
    lookup = load_producer_lookup(config)

    # Process tokenized data
    process_tokenized_data(lookup, batch_size)

    print("\n✅ Done!")


if __name__ == '__main__':
    main()
