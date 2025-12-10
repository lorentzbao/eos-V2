# Contract Data Setup Guide

This guide explains how to set up branch and solicitor data for the 契約 (contract) search mode.

## Overview

The contract search mode uses district-based indexes with hierarchical dropdowns:
1. **地域事業本部 (Regional Office/District)** - Top level
2. **支店 (Branch)** - Second level (filtered by district)
3. **ソリシター (Solicitor)** - Third level (filtered by district)

## Step 1: Prepare Your CSV Data

Create a CSV file with the following columns:
- `DISTRICT_NAME` - District name (e.g., 東京事業本部, 大阪事業本部)
- `BRANCH_CD` - Branch code
- `BRANCH_NAME` - Branch name
- `SOLICITOR_CD` - Solicitor code
- `SOLICITOR` - Solicitor name

**Example CSV:**
```csv
DISTRICT_NAME,BRANCH_CD,BRANCH_NAME,SOLICITOR_CD,SOLICITOR
東京事業本部,001,渋谷支店,S001,山田太郎
東京事業本部,001,渋谷支店,S002,田中花子
東京事業本部,002,新宿支店,S003,佐藤次郎
大阪事業本部,010,梅田支店,S010,鈴木三郎
```

## Step 2: Run the Conversion Script

```bash
python scripts/convert_contract_data_to_json.py data/your_contract_data.csv
```

This will create:
- `data/contract_branches.json`
- `data/contract_solicitors.json`

## Step 3: JSON Output Format

### contract_branches.json
```json
{
  "tokyo": [
    {"code": "001", "name": "渋谷支店"},
    {"code": "002", "name": "新宿支店"}
  ],
  "osaka": [
    {"code": "010", "name": "梅田支店"}
  ]
}
```

### contract_solicitors.json
```json
{
  "tokyo": [
    {"code": "S001", "name": "山田太郎"},
    {"code": "S002", "name": "田中花子"}
  ],
  "osaka": [
    {"code": "S010", "name": "鈴木三郎"}
  ]
}
```

## Step 4: Available API Endpoints

The following API endpoints are now available:

### Get all districts
```
GET /api/districts
Response: {"districts": [{"value": "tokyo", "name": "東京事業本部"}, ...]}
```

### Get branches for a district
```
GET /api/branches/tokyo
Response: {"branches": [{"code": "001", "name": "渋谷支店"}, ...]}
```

### Get solicitors for a district
```
GET /api/solicitors/tokyo
Response: {"solicitors": [{"code": "S001", "name": "山田太郎"}, ...]}
```

## Step 5: Frontend Usage

The frontend can call these APIs to populate dropdowns dynamically:

```javascript
// Load branches when district is selected
const district = 'tokyo';
const response = await fetch(`/api/branches/${district}`);
const data = await response.json();
const branches = data.branches; // [{code: "001", name: "渋谷支店"}, ...]

// Load solicitors when district is selected
const response2 = await fetch(`/api/solicitors/${district}`);
const data2 = await response2.json();
const solicitors = data2.solicitors; // [{code: "S001", name: "山田太郎"}, ...]
```

## District Mapping

The conversion script uses the following district name mapping (can be customized):

| Japanese Name | Key in JSON | Config YAML Key |
|---------------|-------------|-----------------|
| 東京事業本部 | `tokyo` | `tokyo` |
| 大阪事業本部 | `osaka` | `osaka` |
| 名古屋事業本部 | `nagoya` | `nagoya` |
| 九州事業本部 | `kyushu` | `kyushu` |
| 東北事業本部 | `tohoku` | `tohoku` |

## Troubleshooting

### Unknown district warning
If you see: `Warning: Unknown district 'xxx', skipping row`

Add the district to the `DISTRICT_MAPPING` in `scripts/convert_contract_data_to_json.py`:

```python
DISTRICT_MAPPING = {
    "東京事業本部": "tokyo",
    "your_new_district": "your_key",
}
```

### Duplicates
The script automatically removes duplicate branches/solicitors within each district.
