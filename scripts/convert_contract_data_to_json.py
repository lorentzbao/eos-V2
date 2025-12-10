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
                                  branches_output: str = "data/contract_branches.json",
                                  solicitors_output: str = "data/contract_solicitors.json"):
    """
    Convert contract data CSV to JSON format

    Args:
        csv_path: Path to input CSV file
        branches_output: Path to output branches JSON file
        solicitors_output: Path to output solicitors JSON file
    """
    if not os.path.exists(csv_path):
        print(f"Error: Input file '{csv_path}' not found")
        return False

    # Data structures
    district_branches = defaultdict(list)
    district_solicitors = defaultdict(list)

    # Track unique items (to avoid duplicates)
    seen_branches = defaultdict(set)  # district -> set of branch codes
    seen_solicitors = defaultdict(set)  # district -> set of solicitor codes

    # Read CSV file
    print(f"Reading CSV from: {csv_path}")
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)

        for row in reader:
            district_name = row.get('DISTRICT_NAME', '').strip()
            branch_cd = row.get('BRANCH_CD', '').strip()
            branch_name = row.get('BRANCH_NAME', '').strip()
            solicitor_cd = row.get('SOLICITOR_CD', '').strip()
            solicitor_name = row.get('SOLICITOR', '').strip()

            # Map district name to key
            district_key = DISTRICT_MAPPING.get(district_name)
            if not district_key:
                print(f"Warning: Unknown district '{district_name}', skipping row")
                continue

            # Add branch (if exists and not duplicate)
            if branch_cd and branch_name:
                if branch_cd not in seen_branches[district_key]:
                    district_branches[district_key].append({
                        "code": branch_cd,
                        "name": branch_name
                    })
                    seen_branches[district_key].add(branch_cd)

            # Add solicitor (if exists and not duplicate)
            if solicitor_cd and solicitor_name:
                if solicitor_cd not in seen_solicitors[district_key]:
                    district_solicitors[district_key].append({
                        "code": solicitor_cd,
                        "name": solicitor_name
                    })
                    seen_solicitors[district_key].add(solicitor_cd)

    # Sort results
    branches_result = dict(sorted(district_branches.items()))
    for district in branches_result:
        branches_result[district] = sorted(branches_result[district], key=lambda x: x['code'])

    solicitors_result = dict(sorted(district_solicitors.items()))
    for district in solicitors_result:
        solicitors_result[district] = sorted(solicitors_result[district], key=lambda x: x['code'])

    # Write branches JSON
    with open(branches_output, 'w', encoding='utf-8') as f:
        json.dump(branches_result, f, ensure_ascii=False, indent=2)

    # Write solicitors JSON
    with open(solicitors_output, 'w', encoding='utf-8') as f:
        json.dump(solicitors_result, f, ensure_ascii=False, indent=2)

    # Print statistics
    total_branches = sum(len(branches) for branches in branches_result.values())
    total_solicitors = sum(len(solicitors) for solicitors in solicitors_result.values())

    print(f"\n✅ Successfully converted contract data!")
    print(f"\n📁 Branches: {total_branches} total across {len(branches_result)} districts")
    for district, branches in branches_result.items():
        print(f"  - {district}: {len(branches)} branches")

    print(f"\n👤 Solicitors: {total_solicitors} total across {len(solicitors_result)} districts")
    for district, solicitors in solicitors_result.items():
        print(f"  - {district}: {len(solicitors)} solicitors")

    print(f"\n📝 Output files:")
    print(f"  - {branches_output}")
    print(f"  - {solicitors_output}")

    return True

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Usage: python scripts/convert_contract_data_to_json.py <csv_path>")
        print("\nExpected CSV columns: BRANCH_CD, BRANCH_NAME, SOLICITOR_CD, SOLICITOR, DISTRICT_NAME")
        sys.exit(1)

    csv_path = sys.argv[1]
    branches_output = "data/contract_branches.json"
    solicitors_output = "data/contract_solicitors.json"

    # Allow custom output paths
    if len(sys.argv) > 2:
        branches_output = sys.argv[2]
    if len(sys.argv) > 3:
        solicitors_output = sys.argv[3]

    convert_contract_csv_to_json(csv_path, branches_output, solicitors_output)
