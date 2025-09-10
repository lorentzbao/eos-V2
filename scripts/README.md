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

# Using configuration presets (optional)
uv run python scripts/tokenize_csv.py --config-path ../conf/presets --config-name <preset_name>

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

**Configuration Presets:**
- `json_companies` - JSON folder processing with DataFrame merging
- `csv_companies` - Traditional CSV file processing

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

# Using configuration presets
uv run python scripts/tokenize_csv.py --config-path ../conf/presets --config-name json_companies
uv run python scripts/tokenize_csv.py --config-path ../conf/presets --config-name csv_companies

# Preset with overrides
uv run python scripts/tokenize_csv.py --config-path ../conf/presets --config-name json_companies processing.batch_size=1000
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
python scripts/create_index.py --tokenized-dir <tokenized_dir> [--index-dir DIR]

# From CSV (direct)
python scripts/create_index.py <csv_file> [--batch-size SIZE] [--index-dir DIR]
```

**Examples:**
```bash
# Two-step workflow with auto-generated paths
python scripts/tokenize_csv.py --json-folder data/test_json_companies
python scripts/create_index.py --tokenized-dir data/test_json_companies/tokenized

# From CSV with custom index directory
python scripts/create_index.py data/companies.csv --index-dir data/custom_index/

# From tokenized data with custom paths
python scripts/create_index.py --tokenized-dir data/custom/tokenized --index-dir data/custom/index
```

**Features:**
- **Enhanced Type Handling** - Supports both string and integer inputs from JSON data
- **Auto-directory Generation** - Creates index directories based on tokenized data source
- **Progress Monitoring** - Real-time batch processing feedback
- **Error Recovery** - Robust handling of malformed data

### 3. `delete_index.py` - Index Deletion

**Usage:**
```bash
python scripts/delete_index.py [--index-dir DIR] [--force] [--stats-only]
```

### 4. `add_to_index.py` - Add to Existing Index

**Usage:**
```bash
python scripts/add_to_index.py <csv_file> [--batch-size SIZE] [--index-dir DIR] [--dry-run]
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

## Performance & Tips

- **Batch sizes**: 500-1000 for most datasets
- **Two-step approach**: Tokenize first, then index for better performance
- **Memory**: Reduce batch size if encountering memory issues
- **Confirmation**: `delete_index.py` requires confirmation unless `--force`
- **Dry run**: Use `--dry-run` with `add_to_index.py` to preview changes