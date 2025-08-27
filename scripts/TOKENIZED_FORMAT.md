# Tokenized Data Format Specification

This document describes the intermediate JSON format used between the tokenization step (`tokenize_csv.py`) and index creation step (`create_index.py`).

## Directory Structure

```
data/tokenized/
├── tokenization_summary.json       # Processing metadata
├── tokenized_batch_0001.json      # Batch 1 data
├── tokenized_batch_0002.json      # Batch 2 data
└── tokenized_batch_NNNN.json      # Batch N data
```

## Summary File Format

**File:** `tokenization_summary.json`

```json
{
  "processing_info": {
    "total_batches": 5,
    "total_records": 2500,
    "processing_time_seconds": 45.67,
    "records_per_second": 54.8,
    "created_at": "2024-01-15 14:30:25"
  },
  "file_info": {
    "batch_files": [
      "tokenized_batch_0001.json",
      "tokenized_batch_0002.json"
    ],
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

## Batch File Format

**Files:** `tokenized_batch_NNNN.json`

Each batch file contains an array of tokenized records:

```json
[
  {
    // Original CSV fields (preserved)
    "id": "url_001",
    "jcn": "1010001000001",
    "cust_status": "白地",
    "company_name_kj": "株式会社東京テクノロジー",
    "company_address_all": "東京都港区虎ノ門1-1-1",
    "duns_large_class_name": "情報通信業",
    "duns_middle_class_name": "ソフトウェア業",
    "curr_setlmnt_taking_amt": 500000000,
    "employee": 250,
    "prefecture": "tokyo",
    "city": "港区",
    "district_finalized_cd": "TK001",
    "branch_name_cd": "BR001",
    "main_domain_url": "https://tokyo-tech.co.jp",
    "url_name": "メインサイト",
    "url": "https://tokyo-tech.co.jp",
    "content": "東京を拠点とするIT企業です。Python、Java、React開発チームを募集中。",
    "title": "株式会社東京テクノロジー - メインサイト",
    
    // Tokenization results (added)
    "content_tokens": "東京 拠点 企業 python java react 開発 チーム 募集",
    "token_count": 9
  }
]
```

## Field Descriptions

### Required Fields (from CSV)
- `id` - Unique identifier for the document
- `content` - Original text content 
- `content_tokens` - Space-separated tokenized content (searchable)

### Enterprise Fields (preserved from CSV)
All original CSV fields are preserved in the tokenized format, including:
- Corporate identification: `jcn`, `cust_status`, `company_name_kj`
- Address information: `company_address_all`, `prefecture`, `city`
- Industry classification: `duns_large_class_name`, `duns_middle_class_name`
- Financial data: `curr_setlmnt_taking_amt`, `employee`
- Organization codes: `district_finalized_cd`, `branch_name_cd`
- Website information: `main_domain_url`, `url_name`, `url`

### Tokenization Results (added)
- `content_tokens` - Space-separated meaningful tokens for searching
- `token_count` - Number of tokens extracted

## Tokenization Rules

### Included Parts of Speech
- `名詞` (Nouns) - All types of nouns
- `動詞` (Verbs) - Action words  
- `形容詞` (Adjectives) - Descriptive words
- `副詞` (Adverbs) - Manner/degree modifiers

### Filtering Rules
1. **Minimum length:** Words must be > 1 character
2. **Stop words:** Common functional words are filtered out
3. **Case normalization:** All tokens converted to lowercase
4. **Whitespace:** Tokens separated by single spaces

### Stop Words List
Common Japanese function words that are filtered out:
```
する、ある、この、その、あの、という、といった、など、により、
について、において、に関して、に対して、として、による、から、
まで、では、には、にて、での、への、からの、までの
```

## Usage Workflow

### 1. Tokenization Step
```bash
# Process CSV and create tokenized intermediate files
python scripts/tokenize_csv.py data/companies.csv --output-dir data/tokenized/
```

### 2. Index Creation Step  
```bash
# Create search index from tokenized files
python scripts/create_index.py --tokenized-dir data/tokenized/
```

### 3. Benefits of Two-Step Process
- **Preprocessing flexibility:** Modify tokens before indexing
- **Performance:** Reuse tokenized data for multiple indexes
- **Debugging:** Inspect tokenization results before indexing
- **Batch processing:** Handle large datasets efficiently
- **Reproducibility:** Consistent tokenization across runs

## File Naming Convention

- Batch files: `tokenized_batch_NNNN.json` (zero-padded 4 digits)
- Summary file: `tokenization_summary.json`
- Directory: User-configurable (default: `data/tokenized/`)

## Error Handling

- **Missing fields:** Records without required fields are skipped
- **Invalid JSON:** Corrupted batch files are skipped with warnings
- **Empty batches:** Empty or invalid batches are ignored
- **Validation:** Field validation ensures data integrity

## Performance Considerations

- **Batch size:** Affects memory usage and processing speed
- **File size:** Large batches reduce I/O but increase memory usage
- **Encoding:** UTF-8 ensures proper Japanese character handling
- **Compression:** Consider gzip for large datasets (not implemented)

## Integration Notes

The `create_index.py` script automatically detects tokenized input and:
1. Skips re-tokenization for performance
2. Uses `content_tokens` field directly for indexing
3. Preserves original `content` for display purposes
4. Validates tokenized data format before processing