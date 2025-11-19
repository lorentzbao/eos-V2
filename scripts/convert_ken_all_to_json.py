#!/usr/bin/env python3
"""
Convert KEN_ALL.CSV to prefecture_cities.json format.

This script reads the KEN_ALL.CSV file (in Shift-JIS encoding) and converts it
to the JSON format used by the EOS application for city dropdowns.
"""

import csv
import json
from collections import defaultdict
from pathlib import Path

# Mapping from Japanese prefecture names to English keys (from config.yaml)
PREFECTURE_MAPPING = {
    "北海道": "hokkaido",
    "青森県": "aomori",
    "岩手県": "iwate",
    "宮城県": "miyagi",
    "秋田県": "akita",
    "山形県": "yamagata",
    "福島県": "fukushima",
    "茨城県": "ibaraki",
    "栃木県": "tochigi",
    "群馬県": "gunma",
    "埼玉県": "saitama",
    "千葉県": "chiba",
    "東京都": "tokyo",
    "神奈川県": "kanagawa",
    "新潟県": "niigata",
    "富山県": "toyama",
    "石川県": "ishigawa",
    "福井県": "fukui",
    "山梨県": "yamanashi",
    "長野県": "nagano",
    "岐阜県": "gifu",
    "静岡県": "shizuoka",
    "愛知県": "aichi",
    "三重県": "mie",
    "滋賀県": "shiga",
    "京都府": "kyoto",
    "大阪府": "osaka",
    "兵庫県": "hyougo",
    "奈良県": "nara",
    "和歌山県": "wakayama",
    "鳥取県": "tottori",
    "島根県": "shimane",
    "岡山県": "okayama",
    "広島県": "hiroshima",
    "山口県": "yamaguchi",
    "徳島県": "tokushima",
    "香川県": "kagawa",
    "愛媛県": "ehime",
    "高知県": "kochi",
    "福岡県": "fukuoka",
    "佐賀県": "saga",
    "長崎県": "nagasaki",
    "熊本県": "kumamoto",
    "大分県": "oita",
    "宮崎県": "miyazaki",
    "鹿児島県": "kagoshima",
    "沖縄県": "okinawa"
}


def convert_ken_all_to_json(csv_path: str, output_path: str):
    """
    Convert KEN_ALL.CSV to prefecture_cities.json format.

    Args:
        csv_path: Path to KEN_ALL.CSV file
        output_path: Path to output JSON file
    """
    # Read CSV and group cities by prefecture
    prefecture_cities = defaultdict(list)

    print(f"Reading CSV file: {csv_path}")
    with open(csv_path, 'r', encoding='shift_jis') as f:
        reader = csv.DictReader(f)

        for row in reader:
            prefecture_ja = row['prefecture']
            city = row['city']

            # Get English key for prefecture
            prefecture_key = PREFECTURE_MAPPING.get(prefecture_ja)

            if not prefecture_key:
                print(f"Warning: Unknown prefecture '{prefecture_ja}', skipping")
                continue

            # Add city to prefecture (avoid duplicates)
            city_obj = {"value": city, "name": city}
            if city_obj not in prefecture_cities[prefecture_key]:
                prefecture_cities[prefecture_key].append(city_obj)

    # Convert defaultdict to regular dict and sort prefectures by key
    result = dict(sorted(prefecture_cities.items()))

    # Print statistics
    print(f"\nConversion complete!")
    print(f"Total prefectures: {len(result)}")
    total_cities = sum(len(cities) for cities in result.values())
    print(f"Total cities: {total_cities}")

    print(f"\nCities per prefecture:")
    for pref, cities in sorted(result.items(), key=lambda x: len(x[1]), reverse=True)[:10]:
        print(f"  {pref}: {len(cities)} cities")

    # Write JSON file
    print(f"\nWriting JSON file: {output_path}")
    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(result, f, ensure_ascii=False, indent=2)

    print(f"Done! Created {output_path}")


def main():
    # Get project root directory
    script_dir = Path(__file__).parent
    project_root = script_dir.parent

    # Define paths
    csv_path = project_root / "data" / "KEN_ALL.CSV"
    output_path = project_root / "data" / "prefecture_cities.json"

    # Check if CSV file exists
    if not csv_path.exists():
        print(f"Error: CSV file not found at {csv_path}")
        return 1

    # Run conversion
    convert_ken_all_to_json(str(csv_path), str(output_path))

    return 0


if __name__ == "__main__":
    exit(main())
