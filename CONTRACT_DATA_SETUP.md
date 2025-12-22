# Contract Data Setup Guide

This guide explains how to set up branch and solicitor data for the 契約 (contract) search mode.

## Overview

The contract search mode uses district-based indexes with hierarchical dropdowns:
1. **地域事業本部 (Regional Office/District)** - Top level
2. **支店 (Branch)** - Second level (filtered by district)
3. **ソリシター (Solicitor)** - Third level (filtered by branch within district)

## Step 1: Prepare Your CSV Data

Create a CSV file with the following columns:
- `DISTRICT_NAME` - District name (e.g., 北海道・東北地域事業本部)
- `MOTHERBRANCH_CD` - Branch code
- `BRANCH_NAME` - Branch name
- `SOLICITOR_CD` - Solicitor code
- `SOLICITOR` - Solicitor name

**Example CSV:**
```csv
DISTRICT_NAME,MOTHERBRANCH_CD,BRANCH_NAME,SOLICITOR_CD,SOLICITOR
北海道・東北地域事業本部,001,札幌支店,S001,山田太郎
北海道・東北地域事業本部,001,札幌支店,S002,田中花子
北海道・東北地域事業本部,002,仙台支店,S003,佐藤次郎
関西地域事業本部,010,梅田支店,S010,鈴木三郎
```

## Step 2: Run the Conversion Script

```bash
python scripts/convert_contract_data_to_json.py data/your_contract_data.csv
```

This will create a single file:
- `data/contract_data.json`

## Step 3: JSON Output Format

### contract_data.json (Hierarchical Structure)
```json
{
  "A": {
    "name": "北海道・東北地域事業本部",
    "branches": [
      {
        "code": "001",
        "name": "札幌支店",
        "solicitors": [
          {"code": "S001", "name": "山田太郎"},
          {"code": "S002", "name": "田中花子"}
        ]
      },
      {
        "code": "002",
        "name": "仙台支店",
        "solicitors": [
          {"code": "S003", "name": "佐藤次郎"}
        ]
      }
    ]
  },
  "E": {
    "name": "関西地域事業本部",
    "branches": [
      {
        "code": "010",
        "name": "梅田支店",
        "solicitors": [
          {"code": "S010", "name": "鈴木三郎"}
        ]
      }
    ]
  }
}
```

## Step 4: Available API Endpoints

The following API endpoints are now available:

### Get all contract data (one call for everything)
```
GET /api/contract-data
Response: {"data": {/* full hierarchical structure */}}
```

### Get all districts
```
GET /api/districts
Response: {"districts": [{"value": "A", "name": "北海道・東北地域事業本部"}, ...]}
```

### Get branches for a district
```
GET /api/branches/A
Response: {"branches": [{"code": "001", "name": "札幌支店"}, ...]}
```

### Get solicitors for a specific branch in a district
```
GET /api/solicitors/A/001
Response: {"solicitors": [{"code": "S001", "name": "山田太郎"}, ...]}
```

## Step 5: Create Contract Tokenized Data

After setting up the contract data JSON for dropdowns, you need to create district-based tokenized data from the prefecture-based tokenized data.

### Prerequisites
- You must have already run `scripts/tokenize_csv_streaming.py` to create `data/tokenized/{prefecture}/batch_*.json`
- You must have the following files:
  - `data/sample_companies.csv` (dataframe with DOMESTIC_DESCRIMI_NO and PRODUCER_CD)
  - `data/t_producer.csv` (producer data with district/branch/solicitor info)

### Run the Script

```bash
python scripts/create_contract_tokenized.py
```

This script will:
1. Read tokenized data from `data/tokenized/{prefecture}/batch_*.json`
2. Filter only records where `CUST_STATUS2='契約'`
3. Join with `data/sample_companies.csv` and `data/t_producer.csv`
4. Add 5 contract fields to each record: `DISTRICT_NAME`, `MOTHERBRANCH_CD`, `BRANCH_NAME`, `SOLICITOR_CD`, `SOLICITOR`
5. Output to `data/tokenized_contract/{district}/batch_*.json`

### Output Structure
```
data/tokenized_contract/
├── A/
│   ├── batch_0.json
│   ├── batch_1.json
│   └── ...
├── B/
│   ├── batch_0.json
│   └── ...
└── ...
```

Each batch file contains records with all original fields plus the 5 contract-specific fields.

## Step 6: Create Contract Search Indexes

After creating the contract tokenized data, create Whoosh search indexes for each district.

### Create All District Indexes

```bash
python scripts/create_index_contract.py
```

This will create indexes for all districts (A, B, C, ...) found in `data/tokenized_contract/`.

### Create Index for Specific District

```bash
# Create index for district A only
python scripts/create_index_contract.py --district A

# Create index for district E only
python scripts/create_index_contract.py --district E
```

### Clear and Rebuild Indexes

```bash
# Clear and rebuild all indexes
python scripts/create_index_contract.py --clear-existing

# Clear and rebuild specific district
python scripts/create_index_contract.py --district A --clear-existing
```

### Output Structure
```
data/contract_indexes/
├── A/
│   ├── _MAIN_0.toc
│   └── MAIN_*.seg
├── B/
│   └── ...
└── ...
```

### Verify Index Creation

Check the statistics for each district:

```bash
python scripts/index_info.py data/contract_indexes/A
python scripts/index_info.py data/contract_indexes/E
```

## Step 7: Frontend Usage

The frontend can call these APIs to populate dropdowns dynamically:

### Option A: Load all data once (recommended for small datasets)
```javascript
const response = await fetch('/api/contract-data');
const data = await response.json();
const contractData = data.data;

// Then filter locally
const district = 'A';
const branches = contractData[district].branches;
const solicitors = branches.find(b => b.code === '001').solicitors;
```

### Option B: Load data on-demand
```javascript
// Load branches when district is selected
const district = 'A';
const response = await fetch(`/api/branches/${district}`);
const data = await response.json();
const branches = data.branches; // [{code: "001", name: "札幌支店"}, ...]

// Load solicitors when branch is selected
const branch = '001';
const response2 = await fetch(`/api/solicitors/${district}/${branch}`);
const data2 = await response2.json();
const solicitors = data2.solicitors; // [{code: "S001", name: "山田太郎"}, ...]
```

## District Mapping

The conversion script uses the following district name mapping:

| Japanese Name | Key in JSON |
|---------------|-------------|
| 北海道・東北地域事業本部 | A |
| 関信越地域事業本部 | B |
| 首都圏地域事業本部 | C |
| 東海・北陸地域事業本部 | D |
| 関西地域事業本部 | E |
| 中国・四国地域事業本部 | F |
| 九州・沖縄地域事業本部 | G |
| 本店グループ | H |
| 企業営業本部 | I |
| 全国代理店センター本部 | J |
| 企業営業グループ | K |

## Troubleshooting

### Unknown district warning
If you see: `Warning: Unknown district 'xxx', skipping row`

Add the district to the `DISTRICT_MAPPING` in `scripts/convert_contract_data_to_json.py`:

```python
DISTRICT_MAPPING = {
    "北海道・東北地域事業本部": "A",
    "your_new_district": "your_key",
}
```

### Duplicates
The script automatically removes duplicate branches/solicitors within each district.
