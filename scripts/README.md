# EOS Index Management Scripts

Utility scripts for managing Whoosh search indexes with Japanese text processing, HTML content extraction, and flexible data sources.

## Two-Step Workflow (Recommended)

1. **`tokenize_csv.py`** - Tokenize Japanese text with HTML content extraction and preprocessing flexibility
2. **`create_index.py`** - Create search index from tokenized or raw CSV data

### 1. `tokenize_csv.py` - Japanese Text Tokenization & HTML Processing

**Supports both CSV files and JSON folder structures with HTML content extraction.**

**Usage:**
```bash
# CSV input
python scripts/tokenize_csv.py --csv-file <csv_file> [OPTIONS]

# JSON folder input  
python scripts/tokenize_csv.py --json-folder <json_folder> [OPTIONS]
```

**Key Features:**
- **HTML Content Extraction** - Extract and tokenize content from HTML files referenced in JSON data
- **DataFrame Merging** - Merge additional company information from CSV files (O(1) performance)
- **URL-based Records** - Generate separate records for main domains and sub-domains
- **Content Length Control** - Configurable HTML content truncation to prevent overwhelming tokenization
- **Auto-directory Generation** - Smart output directory naming based on input source

**Examples:**
```bash
# JSON folder with HTML content extraction
python scripts/tokenize_csv.py --json-folder data/test_json_companies --max-content-length 10000

# JSON with DataFrame merging for additional company info
python scripts/tokenize_csv.py --json-folder data/companies_json/ --dataframe-file data/company_info.csv

# Traditional CSV processing
python scripts/tokenize_csv.py --csv-file data/companies.csv --batch-size 1000

# Custom output directory and content limits
python scripts/tokenize_csv.py --json-folder data/companies/ --output-dir data/custom/ --max-content-length 5000
```

**Parameters:**
- `--csv-file` - Path to CSV file (mutually exclusive with --json-folder)
- `--json-folder` - Path to folder containing JSON company files  
- `--dataframe-file` - CSV file for merging additional company information (used with --json-folder)
- `--batch-size` - Records per batch (default: 500)
- `--output-dir` - Output directory (auto-generated if not specified)
- `--clear-output` - Clear output directory before processing
- `--max-content-length` - Maximum HTML content length for tokenization (default: 10000)

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