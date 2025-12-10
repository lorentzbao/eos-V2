#!/usr/bin/env python3
"""
Convert contract data (branches and solicitors) from CSV to JSON format

Input CSV columns: BRANCH_CD, BRANCH_NAME, SOLICITOR_CD, SOLICITOR, DISTRICT_NAME
Output:
  - data/contract_branches.json (branches grouped by district)
  - data/contract_solicitors.json (solicitors grouped by district)

Usage:
  python scripts/convert_contract_data_to_json.py <csv_path>
"""

import csv
import json
from collections import defaultdict
import sys
import os

# District name mapping to config key (adjust based on your contract_indexes in config.yaml)
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
    "全国代理店センター本部": "j",
    "企業営業グループ": "K"
}

def convert_contract_csv_to_json(csv_path: str,
                                  output: str = "data/contract_data.json"):
    """
    Convert contract data CSV to single hierarchical JSON format

    Output structure:
    {
      "A": {
        "name": "北海道・東北地域事業本部",
        "branches": [
          {
            "code": "001",
            "name": "札幌支店",
            "solicitors": [
              {"code": "S001", "name": "山田太郎"}
            ]
          }
        ]
      }
    }

    Args:
        csv_path: Path to input CSV file
        output: Path to output JSON file
    """
    if not os.path.exists(csv_path):
        print(f"Error: Input file '{csv_path}' not found")
        return False

    # Reverse mapping for district names
    DISTRICT_NAME_MAPPING = {v: k for k, v in DISTRICT_MAPPING.items()}

    # Data structure: district -> branch_code -> branch data
    contract_data = {}
    branch_data = defaultdict(lambda: defaultdict(lambda: {
        'name': '',
        'solicitors': []
    }))

    # Track seen items to avoid duplicates
    seen_solicitors = defaultdict(lambda: defaultdict(set))  # district -> branch -> set of solicitor codes
    seen_branches = defaultdict(dict)  # district -> {branch_code: branch_name}

    # Statistics
    total_rows = 0
    skipped_rows = 0
    duplicate_branches = 0
    duplicate_solicitors = 0
    branch_name_conflicts = 0

    # Read CSV file
    print(f"Reading CSV from: {csv_path}")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            total_rows += 1
            district_name = row.get('DISTRICT_NAME', '').strip()
            branch_cd = row.get('BRANCH_CD', '').strip()
            branch_name = row.get('BRANCH_NAME', '').strip()
            solicitor_cd = row.get('SOLICITOR_CD', '').strip()
            solicitor_name = row.get('SOLICITOR', '').strip()

            # Skip rows with missing essential data
            if not district_name:
                skipped_rows += 1
                continue

            # Map district name to key
            district_key = DISTRICT_MAPPING.get(district_name)
            if not district_key:
                print(f"Warning: Unknown district '{district_name}' in row {total_rows}, skipping")
                skipped_rows += 1
                continue

            # Store branch info (check for conflicts)
            if branch_cd and branch_name:
                if branch_cd in seen_branches[district_key]:
                    # Branch already exists - check for name conflict
                    existing_name = seen_branches[district_key][branch_cd]
                    if existing_name != branch_name:
                        branch_name_conflicts += 1
                        if branch_name_conflicts <= 5:  # Only show first 5 conflicts
                            print(f"Warning: Branch name conflict for {district_key}/{branch_cd}: '{existing_name}' vs '{branch_name}' (keeping first)")
                else:
                    seen_branches[district_key][branch_cd] = branch_name
                    branch_data[district_key][branch_cd]['name'] = branch_name

            # Add solicitor to branch (with duplicate detection)
            if solicitor_cd and solicitor_name and branch_cd:
                if solicitor_cd in seen_solicitors[district_key][branch_cd]:
                    duplicate_solicitors += 1
                else:
                    branch_data[district_key][branch_cd]['solicitors'].append({
                        "code": solicitor_cd,
                        "name": solicitor_name
                    })
                    seen_solicitors[district_key][branch_cd].add(solicitor_cd)

    # Convert to final structure
    for district_key in sorted(branch_data.keys()):
        branches = []
        for branch_cd in sorted(branch_data[district_key].keys()):
            branch_info = branch_data[district_key][branch_cd]
            # Sort solicitors by code
            solicitors = sorted(branch_info['solicitors'], key=lambda x: x['code'])
            branches.append({
                "code": branch_cd,
                "name": branch_info['name'],
                "solicitors": solicitors
            })

        contract_data[district_key] = {
            "name": DISTRICT_NAME_MAPPING.get(district_key, district_key),
            "branches": branches
        }

    # Write to JSON file
    with open(output, 'w', encoding='utf-8') as f:
        json.dump(contract_data, f, ensure_ascii=False, indent=2)

    # Print statistics
    total_branches = 0
    total_solicitors = 0

    print(f"\n✅ Successfully converted contract data!")

    # Input statistics
    print(f"\n📥 Input Statistics:")
    print(f"  - Total rows processed: {total_rows}")
    print(f"  - Rows skipped (invalid/unknown district): {skipped_rows}")
    print(f"  - Valid rows: {total_rows - skipped_rows}")

    # Duplicate statistics
    if duplicate_solicitors > 0 or branch_name_conflicts > 0:
        print(f"\n🔄 Duplicates Removed:")
        if duplicate_solicitors > 0:
            print(f"  - Duplicate solicitors: {duplicate_solicitors}")
        if branch_name_conflicts > 0:
            print(f"  - Branch name conflicts: {branch_name_conflicts} (first name kept)")

    # Output statistics by district
    print(f"\n📊 Output Statistics by District:")
    for district_key, district_info in contract_data.items():
        num_branches = len(district_info['branches'])
        num_solicitors = sum(len(b['solicitors']) for b in district_info['branches'])
        total_branches += num_branches
        total_solicitors += num_solicitors
        print(f"  {district_key} ({district_info['name']})")
        print(f"    - Branches: {num_branches}")
        print(f"    - Solicitors: {num_solicitors}")

    print(f"\n📁 Total Output: {total_branches} unique branches, {total_solicitors} unique solicitors across {len(contract_data)} districts")
    print(f"\n📝 Output file: {output}")

    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/convert_contract_data_to_json.py <csv_path> [output_path]")
        print("\nExpected CSV columns: DISTRICT_NAME, BRANCH_CD, BRANCH_NAME, SOLICITOR_CD, SOLICITOR")
        print("\nDefault output: data/contract_data.json")
        sys.exit(1)

    csv_path = sys.argv[1]
    output = "data/contract_data.json"

    # Allow custom output path
    if len(sys.argv) > 2:
        output = sys.argv[2]

    convert_contract_csv_to_json(csv_path, output)
