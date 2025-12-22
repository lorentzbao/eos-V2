# EOS Index Management Scripts

Utility scripts for managing Whoosh search indexes with Japanese text processing, HTML content extraction, and flexible data sources.

## Two-Step Workflow (Recommended)

1. **`tokenize_csv.py`** - Tokenize Japanese text with HTML content extraction and preprocessing flexibility
2. **`create_index.py`** - Create search index from tokenized or raw CSV data

### 1. `tokenize_csv.py` - Japanese Text Tokenization & HTML Processing

**Supports both CSV files and JSON folder structures with HTML content extraction, now using Hydra configuration management.**

**Usage:**
```bash
# Basic usage with direct parameters (like run.py)
uv run python scripts/tokenize_csv.py <key>=<value>

# Using configuration files (optional)
uv run python scripts/tokenize_csv.py --config-name <config_name>

# With command-line overrides
uv run python scripts/tokenize_csv.py <key>=<value> <key2>=<value2>
```

**Key Features:**
- **Hydra Configuration** - YAML-based configuration with command-line overrides
- **HTML Content Extraction** - Extract and tokenize content from HTML files referenced in JSON data
- **DataFrame Merging** - Merge additional company information from CSV files (O(1) performance)
- **URL-based Records** - Generate separate records for main domains and sub-domains
- **Content Length Control** - Configurable HTML content truncation with direct text slicing
- **Auto-directory Generation** - Smart output directory naming based on input source
- **Column Selection** - Specify which DataFrame columns to merge with `extra_columns` list
- **Multiprocessing Support** - Parallel tokenization for improved performance on large datasets

**Configuration Files:**
- `json_companies` - JSON folder processing with DataFrame merging
- `csv_companies` - Traditional CSV file processing
- `tokenize` - Base tokenization configuration

**Performance Optimization:**
- **Hybrid Pipeline**: Combines concurrent I/O with multiprocessing for optimal performance
  - **ThreadPoolExecutor** for I/O-bound file reading operations
  - **ProcessPoolExecutor** for CPU-bound HTML parsing and tokenization
  - Best for datasets with many HTML files or complex HTML content
- **Multiprocessing**: CPU-intensive parallel processing for tokenization
- **Single-threaded**: Better for small datasets (<1000 records) due to reduced overhead
- **Auto-detection**: Set `num_processes: null` to automatically use all CPU cores
- **Batch Size**: Larger batches (1000-5000) work better with multiprocessing

**Examples:**
```bash
# Basic CSV processing
uv run python scripts/tokenize_csv.py input.csv_file=data/sample_companies.csv

# JSON folder with DataFrame merging
uv run python scripts/tokenize_csv.py input.json_folder=data/test_json_companies input.dataframe_file=data/test_company_info.csv

# Override processing settings  
uv run python scripts/tokenize_csv.py input.csv_file=data/sample.csv processing.batch_size=1000 processing.max_content_length=5000

# Select specific DataFrame columns
uv run python scripts/tokenize_csv.py input.json_folder=data/companies input.dataframe_file=data/info.csv processing.extra_columns=[cust_status,revenue]

# Enable high-performance processing
uv run python scripts/tokenize_csv.py input.json_folder=data/companies processing.use_hybrid_pipeline=true processing.num_processes=8

# Using configuration files
uv run python scripts/tokenize_csv.py --config-name json_companies
uv run python scripts/tokenize_csv.py --config-name csv_companies

# Configuration with overrides
uv run python scripts/tokenize_csv.py --config-name json_companies processing.batch_size=1000
```

**Configuration Structure:**
```yaml
input:
  csv_file: null                    # Path to CSV file
  json_folder: "data/companies"     # Path to JSON folder
  dataframe_file: "data/info.csv"   # DataFrame for merging
  
processing:
  batch_size: 500                   # Records per batch
  max_content_length: 10000         # HTML content limit
  extra_columns:                    # DataFrame columns to merge
    - cust_status
    - revenue
  use_multiprocessing: true         # Enable parallel processing
  num_processes: null               # CPU cores (null = auto-detect)
  use_hybrid_pipeline: true        # Enable hybrid async I/O + multiprocessing pipeline
  max_concurrent_io: 20             # Maximum concurrent I/O operations
  
output:
  output_dir: null                  # Auto-generated if null
  clear_output: false
```

### 2. `create_index.py` - Index Creation

**Creates Whoosh search indexes from tokenized data or CSV files with enhanced error handling.**

**Usage:**
```bash
# From tokenized data (recommended)
uv run python scripts/create_index.py --tokenized-dir <tokenized_dir> [--index-dir DIR]

# From CSV (direct)
uv run python scripts/create_index.py <csv_file> [--batch-size SIZE] [--index-dir DIR]
```

**Examples:**
```bash
# Two-step workflow with auto-generated paths
uv run python scripts/tokenize_csv.py --json-folder data/test_json_companies
uv run python scripts/create_index.py --tokenized-dir data/test_json_companies/tokenized

# From CSV with custom index directory
uv run python scripts/create_index.py data/companies.csv --index-dir data/custom_index/

# From tokenized data with custom paths
uv run python scripts/create_index.py --tokenized-dir data/custom/tokenized --index-dir data/custom/index
```

**Features:**
- **Enhanced Type Handling** - Supports both string and integer inputs from JSON data
- **Auto-directory Generation** - Creates index directories based on tokenized data source
- **Progress Monitoring** - Real-time batch processing feedback
- **Error Recovery** - Robust handling of malformed data

### 3. `delete_index.py` - Index Deletion

**Usage:**
```bash
uv run python scripts/delete_index.py [--index-dir DIR] [--force] [--stats-only]
```

### 4. `add_to_index.py` - Add to Existing Index

**Usage:**
```bash
uv run python scripts/add_to_index.py <csv_file> [--batch-size SIZE] [--index-dir DIR] [--dry-run]
```

## Data Processing Pipeline

### **JSON Company Data Structure**
```json
{
  "jcn": 1234567890001,
  "company_name": {"kj": "株式会社テック", "en": "Tech Co."},
  "company_address": {"all": "東京都渋谷区...", "prefecture": "東京都"},
  "company_info": {"employee": 50, "industry": "情報通信業"},
  "homepage": {
    "main_domain": {
      "url": "https://example.com",
      "html_path": "data/HTML/2025/Homepage/example.html"
    },
    "sub_domain": [
      {
        "url": "https://example.com/products",
        "html_path": "data/HTML/2025/Homepage/example_products.html",
        "tags": ["製品情報", "技術"]
      }
    ]
  }
}
```

### **URL-based Record Generation**
Each JSON company file generates multiple records:
- **Main Domain Record** - From `homepage.main_domain`
- **Sub-domain Records** - From each `homepage.sub_domain` entry
- **HTML Content Extraction** - Text extracted from `html_path` fields using BeautifulSoup

### **Tokenized Format**

The two-step workflow creates intermediate JSON files:
```
data/source_name/tokenized/
├── tokenization_summary.json
├── tokenized_batch_0001.json
└── tokenized_batch_NNNN.json
```

**Format Details:** See [TOKENIZED_FORMAT.md](./TOKENIZED_FORMAT.md)

## CSV Format

**Required Fields:** `id`, `jcn`, `company_name_kj`, `url`, `content`

**Optional Fields:** Enterprise data including customer status, address, industry classification, financial data, organization codes, etc.

## Contract Data Processing (契約モード)

For contract (契約) search mode, you need to process data differently to create district-based indexes.

### Overview

Contract data processing involves:
1. Converting branch/solicitor CSV to hierarchical JSON for dropdowns
2. Creating district-based tokenized data from prefecture-based data
3. Building district-based search indexes

### 5. `convert_contract_data_to_json.py` - Contract Data Conversion

Converts CSV with branch/solicitor data to hierarchical JSON for frontend dropdowns.

**Usage:**
```bash
python scripts/convert_contract_data_to_json.py <csv_file> [--output OUTPUT]
```

**Input CSV Format:**
- `DISTRICT_NAME` - District name (e.g., 北海道・東北地域事業本部)
- `MOTHERBRANCH_CD` - Branch code
- `BRANCH_NAME` - Branch name
- `SOLICITOR_CD` - Solicitor code
- `SOLICITOR` - Solicitor name

**Output:** Creates `data/contract_data.json` with hierarchical structure:
```json
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
```

**Example:**
```bash
python scripts/convert_contract_data_to_json.py data/t_producer.csv
```

### 6. `create_contract_tokenized.py` - Contract Tokenized Data Creation

Creates district-based tokenized data from prefecture-based tokenized data.

**Usage:**
```bash
python scripts/create_contract_tokenized.py
```

**Prerequisites:**
- Prefecture-based tokenized data in `data/tokenized/{prefecture}/batch_*.json`
- `data/sample_companies.csv` (DOMESTIC_DESCRIMI_NO, PRODUCER_CD)
- `data/t_producer.csv` (producer data with district/branch/solicitor info)
- Configuration in `conf/json_companies.yaml`

**What it does:**
1. Reads tokenized data from `data/tokenized/{prefecture}/batch_*.json`
2. Filters only records where `CUST_STATUS2='契約'`
3. Joins with dataframe and t_producer.csv using:
   - `DOMESTIC_DESCRIMI_NO` → `PRODUCER_CD` → `PRODUCER_CD_ML`
4. Adds 5 contract fields: `DISTRICT_NAME`, `MOTHERBRANCH_CD`, `BRANCH_NAME`, `SOLICITOR_CD`, `SOLICITOR`
5. Outputs to `data/tokenized_contract/{district}/batch_*.json`

**Configuration (conf/json_companies.yaml):**
```yaml
input:
  dataframe_file: "data/sample_companies.csv"
  t_producer_file: "data/t_producer.csv"

processing:
  batch_size: 256
```

**Output Structure:**
```
data/tokenized_contract/
├── A/
│   ├── batch_0.json
│   ├── batch_1.json
│   └── ...
├── B/
└── ...
```

### 7. `create_index_contract.py` - Contract Index Creation

Creates district-based Whoosh search indexes for contract data.

**Usage:**
```bash
# Create all district indexes
python scripts/create_index_contract.py

# Create specific district
python scripts/create_index_contract.py --district A

# Clear and rebuild
python scripts/create_index_contract.py --clear-existing
python scripts/create_index_contract.py --district A --clear-existing
```

**Options:**
- `--district DISTRICT` - Process specific district (A, B, C, ...)
- `--tokenized-dir DIR` - Base directory for tokenized data (default: `data/tokenized_contract`)
- `--index-dir DIR` - Base directory for indexes (default: `data/contract_indexes`)
- `--clear-existing` - Clear existing indexes before creating

**Output Structure:**
```
data/contract_indexes/
├── A/
│   ├── _MAIN_0.toc
│   └── MAIN_*.seg
├── B/
└── ...
```

**District Mapping:**
- A: 北海道・東北地域事業本部
- B: 関信越地域事業本部
- C: 首都圏地域事業本部
- D: 東海・北陸地域事業本部
- E: 関西地域事業本部
- F: 中国・四国地域事業本部
- G: 九州・沖縄地域事業本部
- H: 本店グループ
- I: 企業営業本部
- J: 全国代理店センター本部
- K: 企業営業グループ

**Example Workflow:**
```bash
# 1. Convert contract data CSV to JSON (for dropdowns)
python scripts/convert_contract_data_to_json.py data/t_producer.csv

# 2. Create district-based tokenized data
python scripts/create_contract_tokenized.py

# 3. Create search indexes for all districts
python scripts/create_index_contract.py

# 4. Verify indexes
python scripts/index_info.py data/contract_indexes/A
python scripts/index_info.py data/contract_indexes/E
```

## Service Architecture

### Prefecture Mode (白地・過去)
- `whoosh_prefecture.py` - Whoosh schema for prefecture-based search
- `search_service_prefecture.py` - Single prefecture search operations
- `multi_prefecture_search_service.py` - Multi-prefecture search management

### Contract Mode (契約)
- `whoosh_contract.py` - Whoosh schema with contract fields (MOTHERBRANCH_CD, SOLICITOR_CD)
- `search_service_contract.py` - Single district search operations
- `multi_contract_search_service.py` - Multi-district search management

## Performance & Tips

- **Batch sizes**: 500-1000 for most datasets, 256 for contract data
- **Two-step approach**: Tokenize first, then index for better performance
- **Memory**: Reduce batch size if encountering memory issues
- **Confirmation**: `delete_index.py` requires confirmation unless `--force`
- **Dry run**: Use `--dry-run` with `add_to_index.py` to preview changes
- **Contract data**: Use streaming approach (Option B) for memory efficiency
- **Index verification**: Always verify indexes with `index_info.py` after creation