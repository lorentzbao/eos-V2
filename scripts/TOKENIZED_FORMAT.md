# Tokenized Format Specification

Intermediate JSON format for two-step tokenization workflow.

## Directory Structure

```
data/tokenized/
├── tokenization_summary.json
├── tokenized_batch_0001.json
└── tokenized_batch_NNNN.json
```

## Summary File

**File:** `tokenization_summary.json` - Processing metadata including batch count, total records, timing, and tokenizer settings.

## Batch Files

**Files:** `tokenized_batch_NNNN.json` - Arrays of tokenized records with:
- Original CSV fields preserved
- Added tokenization results: `content_tokens` (space-separated) and `token_count`

## Tokenization Rules

**Included POS:** Nouns, verbs, adjectives, adverbs (Japanese: 名詞, 動詞, 形容詞, 副詞)

**Filtering:** 
- Minimum 2 characters
- Stop words removed
- Case normalized to lowercase
- Space-separated tokens

## Usage

```bash
# 1. Tokenize CSV
python scripts/tokenize_csv.py data/companies.csv

# 2. Create index from tokens
python scripts/create_index.py --tokenized-dir data/companies/tokenized/
```

**Benefits:** Preprocessing flexibility, reusable tokenized data, better performance.