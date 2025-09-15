# Tokenized Format Specification

Intermediate JSON format for two-step tokenization workflow with HTML content extraction support.

## Directory Structure

```
data/{source_name}/tokenized/
├── tokenization_summary.json
├── tokenized_batch_0001.json
└── tokenized_batch_NNNN.json
```

**Auto-generated Paths:**
- CSV input: `data/{csv_filename}/tokenized/`  
- JSON folder: `data/{folder_name}/tokenized/`

## Summary File

**File:** `tokenization_summary.json` - Processing metadata including:
- Batch count and total records processed
- Processing time and performance metrics  
- Tokenizer settings (POS filters, word length, stop words)
- Creation timestamp

```json
{
  "processing_info": {
    "total_batches": 1,
    "total_records": 5,
    "processing_time_seconds": 0.17,
    "records_per_second": 28.76,
    "created_at": "2025-09-11 00:10:50"
  },
  "file_info": {
    "batch_files": ["tokenized_batch_0001.json"],
    "format": "json",
    "encoding": "utf-8"
  },
  "tokenization_settings": {
    "included_pos": ["名詞", "動詞", "形容詞", "副詞"],
    "min_word_length": 2,
    "stop_words_filtered": true,
    "tokenizer": "janome"
  }
}
```

## Batch Files

**Files:** `tokenized_batch_NNNN.json` - Arrays of tokenized records with:

### **From CSV Input:**
- Original CSV fields preserved (id, jcn, company_name_kj, url, etc.)
- Added tokenization results: `content_tokens` (space-separated) and `token_count`

### **From JSON Input (URL-based records):**
- Company information fields (jcn, company_name_kj, company_address_all, etc.)
- URL-specific fields (id, url, url_name)
- HTML-extracted content tokens: `content_tokens` and `token_count`

```json
[
  {
    "jcn": "1234567890001",
    "company_name_kj": "株式会社テックイノベーション",
    "company_address_all": "東京都渋谷区恵比寿1-2-3",
    "prefecture": "東京都", 
    "city": "渋谷区",
    "employee": 50,
    "main_domain_url": "https://www.techinnovation.co.jp",
    "id": "1234567890001_main",
    "url": "https://www.techinnovation.co.jp",
    "url_name": "メインサイト",
    "content_tokens": "株式会社 テック イノベーション ai 開発 未来 創造...",
    "token_count": 81
  }
]
```

## Tokenization Rules

**Included POS:** Nouns, verbs, adjectives, adverbs (Japanese: 名詞, 動詞, 形容詞, 副詞)

**Filtering:** 
- Minimum 2 characters
- Stop words removed
- Case normalized to lowercase
- Space-separated tokens

## HTML Content Extraction

When processing JSON folders, the tokenizer extracts text content from HTML files:

1. **HTML Path Resolution** - Uses `html_path` fields from JSON company data
2. **Content Extraction** - BeautifulSoup removes scripts, styles, and HTML tags  
3. **Text Cleaning** - Normalizes whitespace and removes extra formatting
4. **Length Control** - Truncates content based on `--max-content-length` parameter
5. **Japanese Tokenization** - Applies Janome tokenizer with POS filtering

## Usage Examples

### **JSON Folder with HTML Content**
```bash
# 1. Tokenize JSON companies with HTML extraction (using Hydra configuration)
uv run python scripts/tokenize_csv.py --config-path conf/presets --config-name json_companies

# 2. Create index from tokens  
uv run python scripts/create_index.py --tokenized-dir data/test_json_companies/tokenized/
```

### **Traditional CSV Processing**
```bash
# 1. Tokenize CSV (using Hydra configuration)
uv run python scripts/tokenize_csv.py --config-path conf/presets --config-name csv_companies

# 2. Create index from tokens
uv run python scripts/create_index.py --tokenized-dir data/sample_companies/tokenized/
```

### **DataFrame Merging with Column Selection**
```bash
# Merge specific columns during tokenization
uv run python scripts/tokenize_csv.py --config-path conf/presets --config-name json_companies processing.extra_columns=[cust_status,revenue]

# Override content length and batch size
uv run python scripts/tokenize_csv.py --config-path conf/presets --config-name json_companies processing.max_content_length=5000 processing.batch_size=1000
```

**Benefits:** 
- Preprocessing flexibility with configurable HTML content limits
- Reusable tokenized data for multiple index configurations
- Better performance through O(1) DataFrame merging
- URL-based record generation for comprehensive company coverage