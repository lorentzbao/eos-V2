# EOS Search Engine Index Management Scripts

This folder contains utility scripts for managing Whoosh search indexes in the EOS (Enterprise Online Search) system.

## Scripts Overview

### 1. `create_index.py` - Create New Index
Creates a new Whoosh search index from a CSV file containing enterprise data.

**Usage:**
```bash
python scripts/create_index.py <csv_file> [options]
```

**Options:**
- `--batch-size BATCH_SIZE` : Number of records per batch (default: 500)
- `--index-dir INDEX_DIR` : Index directory path (default: data/whoosh_index)
- `--clear-existing` : Clear existing index before creating new one

**Examples:**
```bash
# Basic usage
python scripts/create_index.py data/companies.csv

# Large dataset with bigger batches
python scripts/create_index.py data/large_dataset.csv --batch-size 1000

# Custom index directory
python scripts/create_index.py data/companies.csv --index-dir data/custom_index

# Replace existing index
python scripts/create_index.py data/companies.csv --clear-existing
```

### 2. `delete_index.py` - Delete Existing Index
Permanently deletes a Whoosh search index. **Use with caution!**

**Usage:**
```bash
python scripts/delete_index.py [options]
```

**Options:**
- `--index-dir INDEX_DIR` : Index directory to delete (default: data/whoosh_index)
- `--force` : Skip confirmation prompt
- `--stats-only` : Show index statistics without deleting

**Examples:**
```bash
# Delete default index (with confirmation)
python scripts/delete_index.py

# Delete custom index without confirmation
python scripts/delete_index.py --index-dir data/old_index --force

# Check index statistics only
python scripts/delete_index.py --stats-only
```

### 3. `add_to_index.py` - Add Documents to Existing Index
Adds new documents from a CSV file to an existing search index.

**Usage:**
```bash
python scripts/add_to_index.py <csv_file> [options]
```

**Options:**
- `--batch-size BATCH_SIZE` : Number of records per batch (default: 500)
- `--index-dir INDEX_DIR` : Index directory path (default: data/whoosh_index)
- `--no-duplicate-check` : Skip duplicate checking for faster processing
- `--dry-run` : Show what would be done without making changes

**Examples:**
```bash
# Add new documents
python scripts/add_to_index.py data/new_companies.csv

# Large batch processing
python scripts/add_to_index.py data/updates.csv --batch-size 1000

# Skip duplicate checking (faster)
python scripts/add_to_index.py data/incremental.csv --no-duplicate-check

# Test run without changes
python scripts/add_to_index.py data/test.csv --dry-run
```

## CSV File Format

All scripts expect CSV files with the following enterprise data structure:

### Required Fields:
- `id` - Unique identifier for each URL/page
- `jcn` - 法人番号 (Corporate Number) 
- `company_name_kj` - 漢字名 (Company name in Kanji)
- `url` - Specific page URL
- `content` - Searchable text content

### Optional Fields:
- `cust_status` - 顧客区分 (Customer status: "白地", "既存")
- `company_address_all` - 住所 (Full address)
- `duns_large_class_name` - 業種大分類 (Major industry classification)
- `duns_middle_class_name` - 業種中分類 (Minor industry classification)
- `curr_setlmnt_taking_amt` - 売上高 (Revenue, numeric)
- `employee` - 従業員数 (Employee count, numeric)
- `prefecture` - 都道府県 (Prefecture)
- `city` - 市区町村 (City/Ward)
- `district_finalized_cd` - 事業本部コード (District code)
- `branch_name_cd` - 支店コード (Branch code)
- `main_domain_url` - ホームページURL (Main website URL)
- `url_name` - URL description/name

### Sample CSV Format:
```csv
id,jcn,cust_status,company_name_kj,company_address_all,duns_large_class_name,duns_middle_class_name,curr_setlmnt_taking_amt,employee,prefecture,city,district_finalized_cd,branch_name_cd,main_domain_url,url_name,url,content
url_001,1010001000001,白地,株式会社東京テクノロジー,東京都港区虎ノ門1-1-1,情報通信業,ソフトウェア業,500000000,250,tokyo,港区,TK001,BR001,https://tokyo-tech.co.jp,メインサイト,https://tokyo-tech.co.jp/index.html,東京を拠点とするIT企業です...
```

## Performance Tips

### Batch Sizes
- **Small datasets (< 10K records)**: 100-500 records per batch
- **Medium datasets (10K-100K records)**: 500-1000 records per batch  
- **Large datasets (> 100K records)**: 1000-2000 records per batch

### Memory Considerations
- Larger batch sizes use more memory but are generally faster
- If you encounter memory issues, reduce the batch size
- Monitor system resources during processing

### Index Directory Structure
```
data/whoosh_index/
├── _MAIN_*.toc          # Table of contents
├── MAIN_*.seg           # Index segments
└── WRITELOCK            # Write lock (if active)
```

## Error Handling

### Common Issues:

1. **"CSV file not found"**
   - Check the file path is correct
   - Ensure you're running from the project root directory

2. **"Missing required columns"**
   - Verify your CSV has all required fields: id, jcn, company_name_kj, url, content
   - Check for typos in column names

3. **"Index directory does not exist"**
   - For `add_to_index.py`, create an index first using `create_index.py`
   - For `delete_index.py`, the directory may already be deleted

4. **"Permission denied"**
   - Ensure you have write permissions to the index directory
   - Check if another process is using the index

5. **Memory errors with large datasets**
   - Reduce the batch size using `--batch-size`
   - Process data in smaller chunks

## Safety Features

### Confirmation Prompts
- `delete_index.py` requires confirmation unless `--force` is used
- Shows index statistics before deletion

### Dry Run Mode
- `add_to_index.py` supports `--dry-run` to preview changes
- Use this to validate your CSV before actual processing

### Duplicate Detection
- `add_to_index.py` automatically skips duplicate document IDs
- Use `--no-duplicate-check` to disable for better performance

## Integration with EOS

These scripts work with the main EOS application:

1. **After creating/updating index**: Restart the web application to use the new index
2. **Search cache**: The application automatically clears caches when documents are added
3. **Index locking**: Don't run scripts while the web application is actively searching

## Troubleshooting

### Debug Mode
Add debug output by modifying the scripts:
```python
import logging
logging.basicConfig(level=logging.DEBUG)
```

### Manual Index Inspection
```bash
# Check index statistics
python scripts/delete_index.py --stats-only

# List directory contents  
ls -la data/whoosh_index/
```

### Recovery
If an index becomes corrupted:
1. Delete the corrupted index: `python scripts/delete_index.py --force`
2. Recreate from source data: `python scripts/create_index.py data/source.csv`

## Contributing

When modifying these scripts:
1. Test with small datasets first
2. Add appropriate error handling
3. Update this README with new options
4. Follow the existing code style and patterns