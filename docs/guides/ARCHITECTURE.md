# Technical Architecture

EOS Japanese Enterprise Search Engine architecture overview.

---

## 🏗️ System Overview

### Core Technologies
- **Backend:** Flask + Whoosh (Japanese full-text search) + Modular Tokenizers (Janome/MeCab)
- **Frontend:** Bootstrap 5 + Vanilla JavaScript (no jQuery dependency)
- **Data Processing:** Pandas + BeautifulSoup4 for HTML content extraction
- **Configuration:** Hydra for flexible configuration management
- **Tokenization:** Abstract tokenizer layer with pluggable backends

### Performance Features
- **Caching:** LRU cache + file-based CSV export caching
- **Search:** O(1) dictionary lookups for data merging
- **Japanese Support:** UTF-8 encoding with proper tokenization
- **Scalability:** Multi-index support for prefecture-based search
- **Flexible I/O:** Configurable root paths with automatic fallback for different environments

---

## 🗂️ Multi-Index Architecture

The application uses **prefecture-based routing** with separate Whoosh indexes for each prefecture.

### Key Components
- `app/services/multi_index_search_service.py` - Routes searches to correct prefecture index
- `app/services/search_service.py` - Single-index search operations
- `conf/config.yaml` - Multi-index configuration

### How It Works
1. User selects a prefecture in the frontend
2. `MultiIndexSearchService.search()` routes to the appropriate prefecture's `SearchService`
3. Each prefecture has its own Whoosh index in `data/indexes/{prefecture}/`
4. Configuration in `conf/config.yaml` defines available prefectures

### Adding New Prefecture
```bash
# 1. Add to conf/config.yaml
indexes:
  new_prefecture:
    dir: "data/indexes/new_prefecture"
    name: "New Prefecture Name"

# 2. Tokenize data
uv run python scripts/tokenize_csv.py input.json_folder=data/raw/new_prefecture

# 3. Create index
uv run python scripts/create_index.py \
  --tokenized-dir data/tokenized/new_prefecture \
  --index-dir data/indexes/new_prefecture

# 4. Restart application
```

---

## 🧩 Tokenization Architecture

EOS uses a modular tokenizer architecture that allows easy switching between different Japanese tokenizers.

### Components

**Abstract Base Layer:**
- `BaseTokenizer` abstract class defines the common interface
- `Token` dataclass provides unified representation

**Pluggable Backends:**
- **Janome** - Pure Python, easy installation (default)
- **MeCab** - C++ based, faster performance (optional)
- Easy to add new tokenizers (Sudachi, Kuromoji, etc.)

**Factory Pattern:**
- `get_tokenizer()` with auto-detection and graceful fallback
- Configuration-based selection

### File Structure
```
app/services/tokenizers/
├── __init__.py           # Package exports
├── base_tokenizer.py     # Abstract base class + Token dataclass
├── janome_tokenizer.py   # Janome adapter
├── mecab_tokenizer.py    # MeCab adapter
└── factory.py            # get_tokenizer() factory function
```

### Usage Example
```python
from app.services.tokenizers import get_tokenizer

# Auto-detect (tries MeCab, falls back to Janome)
tokenizer = get_tokenizer()

# Explicit selection
tokenizer = get_tokenizer('janome')
tokenizer = get_tokenizer('mecab')

# Tokenize and filter
tokens = tokenizer.tokenize_and_filter('日本語のテキスト', min_length=2)
```

---

## 📊 Data Processing Pipeline

### Two-Step Workflow

**Step 1: Tokenization** (`scripts/tokenize_csv.py`)
- Reads raw data (CSV or JSON folders)
- Extracts HTML content using BeautifulSoup
- Tokenizes Japanese text with configurable tokenizer
- Outputs to `data/tokenized/` as JSON batches
- Supports hybrid async I/O + multiprocessing for performance

**Step 2: Index Creation** (`scripts/create_index.py`)
- Reads tokenized JSON batches
- Creates Whoosh index with Japanese schema
- Outputs to `data/indexes/{prefecture}/`

### Why Two-Step?
- **Preprocessing flexibility** - Can re-index without re-tokenizing
- **Better error recovery** - Isolate failures
- **Performance optimization** - Parallel tokenization, then batch indexing

### Data Flow
```
Raw Data → Tokenization → Tokenized JSON → Indexing → Whoosh Index → Search API
(CSV/JSON)   (parallel)    (batched)      (batched)    (Whoosh)     (Flask)
```

---

## 🌐 Flask Application Structure

### Blueprint-based Routing

**Two types of endpoints:**
1. **HTML Pages** (`/search`, `/login`, `/rankings`, `/history`)
   - Server-rendered with Jinja2 templates
   - Traditional form submissions

2. **JSON APIs** (`/api/search`, `/api/prefectures`, `/api/stats`)
   - RESTful endpoints for AJAX
   - Returns JSON data

### Application Initialization Flow
```
run.py
  ↓ (Hydra entry point)
app/__init__.py:create_app()
  ↓ (Flask app factory)
Register Blueprints (main, api)
  ↓
Routes share get_search_service() helper
  ↓
SearchService / MultiIndexSearchService
```

### Service Layer Hierarchy
```
MultiIndexSearchService (prefecture routing)
  ↓
SearchService (single-index operations)
  ↓
Whoosh Index (full-text search)
```

---

## 🔐 Session-Based Authentication

Simple username-based sessions (no password):

```python
# Login check in routes
if 'username' not in session:
    return redirect(url_for('main.login'))

# Username stored in session
session['username'] = request.form.get('username')
```

**Production Note:** Replace with proper authentication system for production use.

---

## 📁 Project Structure

```
eos/
├── app/                          # Flask application
│   ├── __init__.py              # App factory
│   ├── routes/                  # Route blueprints
│   │   ├── main.py             # HTML pages
│   │   └── api.py              # JSON APIs
│   ├── services/                # Business logic
│   │   ├── search_service.py
│   │   ├── multi_index_search_service.py
│   │   ├── query_processor.py
│   │   ├── search_logger.py
│   │   └── tokenizers/         # Modular tokenizer architecture
│   └── templates/               # Jinja2 templates
├── conf/                         # Hydra configuration
│   ├── config.yaml              # Main app config
│   ├── tokenize.yaml            # Tokenization config
│   └── json_companies.yaml      # Processing presets
├── data/                         # Data storage
│   ├── raw/                     # Original data
│   ├── tokenized/               # Intermediate files
│   └── indexes/                 # Whoosh indexes
├── docs/                         # Documentation
│   ├── api/                     # API documentation
│   ├── development/             # Dev guides
│   ├── data/                    # Data/scripts docs
│   └── guides/                  # Project guides
├── scripts/                      # Data processing scripts
│   ├── tokenize_csv.py
│   ├── create_index.py
│   └── index_info.py
└── run.py                        # Application entry point
```

---

## 🚀 Performance Optimizations

### Search Performance
- **LRU caching** on frequently accessed data (requires singleton service)
- **O(1) dictionary lookups** for company data merging (uses `jcn` as key)
- **Batch processing** for large result sets

### Tokenization Performance
- **Multiprocessing:** Parallel tokenization across CPU cores
- **Hybrid pipeline:** ThreadPoolExecutor (I/O) + ProcessPoolExecutor (CPU)
- **Configurable batch sizes:** 256-1000 optimal for most datasets

### CSV Export Performance
- **File-based caching:** MD5 hash of query parameters
- **Cache location:** `data/csv_cache/`
- **No expiration:** Manual cleanup required (consider adding TTL)

---

## 🔄 URL-based Company Grouping

**Data Model:** Each company can have multiple URLs (main domain + sub-domains)

**Grouping Logic:**
1. Search returns individual URL matches
2. Results grouped by `jcn` (company number)
3. Frontend displays one company card with multiple URL entries

**Implementation:** See `app/services/search_service.py:search()` method

---

## 📝 Japanese Text Processing

### Tokenization
- **POS filtering:** 名詞, 動詞, 形容詞, 副詞
- **Minimum word length:** 2 characters
- **Stop words:** Filtered automatically
- **Encoding:** UTF-8 throughout the system

### HTML Content Extraction
- **BeautifulSoup4** for parsing
- **Script/style removal** before text extraction
- **Configurable max length** to prevent memory issues
- **UTF-8 encoding preservation**

---

## 🔌 Extensibility Points

### Adding New Tokenizer
1. Create adapter class extending `BaseTokenizer`
2. Implement `tokenize()` method
3. Add to factory in `tokenizers/factory.py`
4. Update configuration options

### Adding New Search Index
1. Add configuration to `conf/config.yaml`
2. Process and tokenize data
3. Create Whoosh index
4. Restart application

### Adding New API Endpoint
1. Add route to `app/routes/api.py` or `app/routes/main.py`
2. Use `get_search_service()` helper
3. Return JSON or render template
4. Document in API_REFERENCE.md

---

**For detailed implementation guides, see:**
- [Configuration Guide](../../CONFIGURATION.md)
- [Scripts Guide](../data/SCRIPTS_README.md)
- [API Reference](../api/API_REFERENCE.md)

**Last Updated:** 2025-10-08
