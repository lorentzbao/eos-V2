# EOS Index Management Scripts

Utility scripts for managing Whoosh search indexes with Japanese text processing.

## Two-Step Workflow (Recommended)

1. **`tokenize_csv.py`** - Tokenize Japanese text with preprocessing flexibility
2. **`create_index.py`** - Create search index from tokenized or raw CSV data

### 1. `tokenize_csv.py` - Japanese Text Tokenization

**Usage:**
```bash
python scripts/tokenize_csv.py <csv_file> [--batch-size SIZE] [--output-dir DIR]
```

**Examples:**
```bash
# Basic usage (auto-generates data/companies/tokenized/)
python scripts/tokenize_csv.py data/companies.csv

# Custom batch size and output
python scripts/tokenize_csv.py data/large_dataset.csv --batch-size 1000 --output-dir data/custom/
```

### 2. `create_index.py` - Index Creation

**Usage:**
```bash
# From CSV (direct)
python scripts/create_index.py <csv_file> [--batch-size SIZE] [--index-dir DIR]

# From tokenized data (recommended)
python scripts/create_index.py --tokenized-dir <tokenized_dir> [--index-dir DIR]
```

**Examples:**
```bash
# Two-step workflow (auto-generates paths)
python scripts/tokenize_csv.py data/companies.csv
python scripts/create_index.py --tokenized-dir data/companies/tokenized/

# Direct from CSV
python scripts/create_index.py data/companies.csv
```

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

## Tokenized Format

The two-step workflow creates intermediate JSON files:
```
data/tokenized/
├── tokenization_summary.json
├── tokenized_batch_0001.json
└── tokenized_batch_0002.json
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