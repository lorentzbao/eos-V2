# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

EOS is a Japanese enterprise search engine built with Flask and Whoosh, featuring multi-index architecture for prefecture-based search routing. The system uses server-side rendering with Jinja2 templates and provides both HTML pages and JSON APIs.

## Common Commands

### Running the Application
```bash
# Start development server (default: localhost:5000)
uv run python run.py

# Override configuration settings
uv run python run.py app.debug=false app.host=0.0.0.0 app.port=80

# Production mode
export FLASK_ENV=production
uv run python run.py app.debug=false
```

### Data Processing Pipeline

**Two-step workflow (recommended):**

```bash
# Step 1: Tokenize data (supports CSV or JSON folders)
uv run python scripts/tokenize_csv.py --config-name json_companies
uv run python scripts/tokenize_csv.py input.json_folder=data/raw/tokyo

# Step 2: Create search index
uv run python scripts/create_index.py --tokenized-dir data/tokenized/tokyo --index-dir data/indexes/tokyo

# Verify index
uv run python scripts/index_info.py
```

**Single-step (direct from CSV):**
```bash
uv run python scripts/create_index.py data/companies.csv --batch-size 500
```

### Index Management
```bash
# Add data to existing index
uv run python scripts/add_to_index.py data/new_companies.csv

# Delete index (with confirmation)
uv run python scripts/delete_index.py

# Optimize index
# Use API endpoint: POST /api/optimize_index
```

### Testing
```bash
# Run all tests
uv run pytest

# Run specific test files
uv run pytest tests/test_search_engine.py
uv run pytest tests/test_api_routes.py

# Run with verbose output
uv run pytest -v
```

## Architecture Overview

### Multi-Index System

The application uses **prefecture-based routing** with separate Whoosh indexes for each prefecture. This is the core architectural pattern:

**Key files:**
- `app/services/multi_index_search_service.py` - Routes searches to correct prefecture index
- `app/services/search_service.py` - Single-index search operations (wrapped by multi-index)
- `conf/config.yaml` - Multi-index configuration

**How it works:**
1. User selects a prefecture in the frontend
2. `MultiIndexSearchService.search()` routes to the appropriate prefecture's `SearchService`
3. Each prefecture has its own Whoosh index in `data/indexes/{prefecture}/`
4. Configuration in `conf/config.yaml` defines available prefectures

**Important pattern:**
```python
# Routes check for multi-index vs single-index configuration
def get_search_service():
    if 'INDEXES' in current_app.config:
        return MultiIndexSearchService(current_app.config['INDEXES'])
    else:
        # Fallback to single index (backward compatibility)
        return SearchService(current_app.config['INDEX_DIR'])
```

### Flask Application Structure

**Blueprint-based routing:**
- `app/routes/main.py` - HTML pages (server-rendered with Jinja2)
- `app/routes/api.py` - JSON APIs (for JavaScript/AJAX)

**Two types of endpoints:**
1. **HTML Pages** (`/search`, `/login`, `/rankings`, `/history`) - Server-rendered forms and pages
2. **JSON APIs** (`/api/search`, `/api/prefectures`, `/api/stats`) - AJAX consumption

**Application initialization flow:**
1. `run.py` - Hydra entry point, loads configuration
2. `app/__init__.py:create_app()` - Flask app factory, registers blueprints
3. Blueprints register routes and share `get_search_service()` helper

### Data Processing Architecture

**Two-step tokenization workflow:**

1. **Tokenization** (`scripts/tokenize_csv.py`)
   - Reads raw data (CSV or JSON folders)
   - Extracts HTML content using BeautifulSoup
   - Tokenizes Japanese text with Janome
   - Outputs to `data/tokenized/` as JSON batches
   - Supports hybrid async I/O + multiprocessing for performance

2. **Index Creation** (`scripts/create_index.py`)
   - Reads tokenized JSON batches
   - Creates Whoosh index with Japanese schema
   - Outputs to `data/indexes/{prefecture}/`

**Why two-step?**
- Preprocessing flexibility (can re-index without re-tokenizing)
- Better error recovery
- Performance optimization (parallel tokenization, then batch indexing)

### Hydra Configuration System

**Critical pattern:** All scripts use Hydra for configuration management (like `run.py`).

**Configuration hierarchy:**
- `conf/config.yaml` - Flask app defaults (multi-index setup)
- `conf/json_companies.yaml` - JSON processing preset
- `conf/csv_companies.yaml` - CSV processing preset
- `conf/tokenize.yaml` - Base tokenization config

**Usage pattern:**
```python
@hydra.main(version_base=None, config_path="conf", config_name="config")
def main(cfg: DictConfig) -> None:
    # Access config: cfg.app.debug, cfg.indexes.tokyo.dir, etc.
```

**Command-line overrides:**
```bash
# Override any config value
uv run python run.py app.debug=false indexes.tokyo.dir=data/custom/tokyo
uv run python scripts/tokenize_csv.py processing.batch_size=1000
```

### Search Service Layer

**Service hierarchy:**
- `MultiIndexSearchService` - Prefecture routing (wraps multiple SearchServices)
- `SearchService` - Single-index operations (Whoosh interactions)
- `QueryProcessor` - Query parsing and tokenization
- `SearchLogger` - Search history and analytics

**Key methods:**
- `search(query, prefecture, limit, cust_status)` - Main search with filters
- `get_stats(prefecture)` - Index statistics
- `add_document()` / `add_documents_batch()` - Document management
- `clear_index()` / `optimize_index()` - Index maintenance

**Important:** Multi-index service requires prefecture parameter. Check for `isinstance(search_service, MultiIndexSearchService)` when adding features.

## Critical Patterns

### Session-Based Authentication

Simple username-based sessions (no password):
```python
# Login check in routes
if 'username' not in session:
    return redirect(url_for('main.login'))

# Username stored in session
session['username'] = request.form.get('username')
```

### CSV Export with File Caching

**Performance optimization:** Generated CSVs are cached by query hash to avoid regenerating identical exports.

```python
# Cache key generation
cache_key = hashlib.md5(f"{query}:{prefecture}:{cust_status}".encode('utf-8')).hexdigest()
cache_file = f"data/csv_cache/{cache_key}.csv"

# Serve cached file if exists, otherwise generate and cache
if os.path.exists(cache_file):
    return send_file(cache_file, as_attachment=True)
```

**Location:** `app/routes/api.py:download_csv()`

### Japanese Text Processing

**Tokenization with Janome:**
- POS filtering: 名詞, 動詞, 形容詞, 副詞
- Minimum word length: 2 characters
- Stop words filtered

**UTF-8 encoding critical:**
- All CSV operations use `encoding='utf-8-sig'` (Excel compatibility)
- HTML content extraction preserves Japanese characters

### URL-based Company Grouping

**Core data model:** Each company can have multiple URLs (main domain + sub-domains).

**Grouping logic:**
1. Search returns individual URL matches
2. Results grouped by `jcn` (company number)
3. Frontend displays one company card with multiple URL entries

**Implementation:** `app/services/search_service.py` - see `search()` method's grouping logic

## Data Folder Structure

```
data/
├── raw/                    # Original data files
│   ├── tokyo/             # Prefecture-organized JSON folders
│   ├── osaka/
│   └── kochi/
├── tokenized/             # Intermediate tokenized files
│   ├── tokyo/
│   │   ├── tokenization_summary.json
│   │   └── tokenized_batch_*.json
│   └── ...
├── indexes/               # Whoosh search indexes
│   ├── tokyo/
│   ├── osaka/
│   └── kochi/
├── csv_cache/             # Cached CSV exports
└── sample_companies.csv   # Test data
```

## Important Configuration Details

### Multi-Index Configuration

**File:** `conf/config.yaml`

```yaml
indexes:
  tokyo:
    dir: "data/indexes/tokyo"
    name: "Tokyo"
  osaka:
    dir: "data/indexes/osaka"
    name: "Osaka"
```

**Adding new prefecture:**
1. Add entry to `conf/config.yaml`
2. Tokenize data: `uv run python scripts/tokenize_csv.py input.json_folder=data/raw/{prefecture}`
3. Create index: `uv run python scripts/create_index.py --tokenized-dir data/tokenized/{prefecture} --index-dir data/indexes/{prefecture}`
4. Restart application

### Tokenization Configuration

**Key settings for performance tuning:**

```yaml
processing:
  batch_size: 256                  # Lower = less memory, higher = faster
  max_content_length: 5000         # HTML content truncation
  use_multiprocessing: true        # Enable parallel processing
  num_processes: null              # Auto-detect CPU cores
  use_hybrid_pipeline: true        # Async I/O + multiprocessing
  max_concurrent_io: 8             # I/O parallelism
```

**When to adjust:**
- Large datasets (>10K records): Increase batch_size to 1000-5000
- Memory constraints: Decrease batch_size to 100-256
- Many HTML files: Enable hybrid_pipeline
- CPU-bound: Increase num_processes

## Frontend Development Notes

### Server-Side Rendering Pattern

**Jinja2 templates** generate HTML on the server, NOT client-side React/Vue.

**Template structure:**
- `templates/index.html` - Main search page
- `templates/search.html` - Search results
- `templates/login.html` - Login page
- `templates/rankings.html` - Popular searches
- `templates/history.html` - User search history

**Key Jinja2 patterns:**
```html
<!-- URL generation -->
<form action="{{ url_for('main.search') }}" method="GET">

<!-- Data display -->
<h2>{{ company.company_name_kj }}</h2>

<!-- Loops -->
{% for url in company.urls %}
  <a href="{{ url.url }}">{{ url.url_name }}</a>
{% endfor %}
```

### JavaScript/AJAX Integration

**Use JSON APIs from JavaScript, NOT HTML pages:**

```javascript
// Good: Fetch JSON data
const response = await fetch('/api/search?q=Python&prefecture=tokyo');
const data = await response.json();

// Bad: Don't fetch HTML pages with AJAX
const response = await fetch('/search?q=Python');  // Returns HTML
```

**Common patterns:**
- Dropdown population: `/api/prefectures`
- Dynamic search: `/api/search`
- CSV download trigger: `/api/download-csv`

## Testing Considerations

### Test Data

**Location:** `data/test_json_companies/`

Sample JSON structure mirrors production format with `jcn`, `company_name`, `homepage`, etc.

### Running Tests

Tests cover:
- Search engine functionality
- API endpoint responses
- Tokenization behavior
- Multi-index routing

**Test files:**
- `tests/test_search_engine.py` - Core search logic
- `tests/test_api_routes.py` - API endpoints
- `tests/test_tokenization_behavior.py` - Japanese text processing
- `tests/test_whoosh_search.py` - Whoosh integration

## Common Gotchas

1. **Prefecture parameter required:** Multi-index searches fail without prefecture selection
2. **Hydra output folders:** Script runs create `outputs/` folders (gitignored) with config snapshots
3. **CSV encoding:** Always use `utf-8-sig` for Excel compatibility with Japanese text
4. **Index locking:** Only one writer can access Whoosh index at a time
5. **Session secret:** Change `app.secret_key` in production (conf/config.yaml)
6. **Backward compatibility:** Code maintains single-index fallback for older configurations

## Performance Optimization

### Search Performance
- **LRU caching** on frequently accessed data
- **O(1) dictionary lookups** for company data merging (uses `jcn` as key)
- **Batch processing** for large result sets

### Tokenization Performance
- **Multiprocessing:** Parallel tokenization across CPU cores
- **Hybrid pipeline:** ThreadPoolExecutor (I/O) + ProcessPoolExecutor (CPU)
- **Batch sizes:** 256-1000 optimal for most datasets

### CSV Export Performance
- **File-based caching:** MD5 hash of query parameters
- **Cache location:** `data/csv_cache/`
- **No expiration:** Manual cleanup required

## Deployment Notes

### Production Checklist
1. Set `app.debug=false` in config or via CLI override
2. Change `app.secret_key` to secure random value
3. Set `FLASK_ENV=production` environment variable
4. Configure host/port: `uv run python run.py app.host=0.0.0.0 app.port=80`
5. Ensure all prefecture indexes are built and optimized
6. Set up proper logging and monitoring

### Data Migration
When moving data between environments:
1. Copy `data/indexes/` folders (NOT individual files)
2. Copy `data/tokenized/` if re-indexing needed
3. Verify index integrity: `uv run python scripts/index_info.py`
4. Update `conf/config.yaml` paths if needed

## Documentation References

- **Frontend:** `FRONTEND_DEVELOPMENT.md` - Complete UI/UX guide
- **API:** `app/API_REFERENCE.md` - All endpoints with examples
- **Scripts:** `scripts/README.md` - Data processing workflow
- **Configuration:** `CONFIGURATION.md` - Hydra setup and options
- **Data Format:** `scripts/TOKENIZED_FORMAT.md` - Tokenized JSON structure
