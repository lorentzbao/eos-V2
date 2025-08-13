# Japanese Search Engine

A Flask-based search engine designed specifically for Japanese text processing using Janome tokenization and TF-IDF scoring.

## Project Overview

This search engine provides full-text search capabilities for Japanese documents with a clean web interface and REST API. It uses Janome for Japanese tokenization and implements TF-IDF scoring for relevance ranking.

## Project Structure

```
search_engine/
├── app/                          # Flask application package
│   ├── __init__.py              # App factory with blueprint registration
│   ├── routes/                  # URL routes and endpoints
│   │   ├── __init__.py
│   │   ├── main.py             # Web interface routes (/, /search)
│   │   └── api.py              # REST API routes (/api/*)
│   ├── services/               # Core search logic
│   │   ├── simple_search.py    # Custom Japanese search with TF-IDF
│   │   ├── whoosh_simple.py    # Whoosh-based search implementation
│   │   ├── query_processor.py  # Query parsing and processing
│   │   ├── search_service.py   # Main search service (uses Whoosh)
│   │   ├── search_service_whoosh.py # Alternative Whoosh service
│   │   └── japanese_text_processor.py # Text processing utilities
│   ├── models/                 # Data models (empty for now)
│   └── utils/                  # Utility functions (empty for now)
├── templates/                  # HTML templates
│   ├── base.html              # Base template with Bootstrap
│   ├── index.html             # Main search page
│   └── search.html            # Search results page
├── static/                    # Static assets
│   ├── css/
│   │   └── style.css          # Custom styles
│   └── js/
│       └── search.js          # Frontend JavaScript
├── data/                      # Data storage
│   ├── search_index.json      # JSON-based search index
│   └── documents/             # Document storage (empty)
├── tests/                     # Test suite
│   ├── __init__.py           # Test package
│   ├── test_search_engine.py # Main search engine tests
│   ├── test_whoosh_simple.py # Whoosh implementation tests
│   ├── test_api_routes.py    # API endpoint tests
│   ├── test_tokenization_behavior.py # Tokenization tests
│   └── compare_implementations.py # Engine comparison
├── requirements.txt           # Python dependencies
├── run.py                     # Application entry point
└── README.md                  # This documentation
```

## Key Components

### 1. Search Engine Implementations

#### Custom Implementation (`simple_search.py`)
- **Japanese tokenization** using Janome
- **Custom TF-IDF scoring** for relevance ranking  
- **Inverted index** for fast lookups
- **JSON persistence** for data storage
- **Lightweight and educational**

#### Whoosh Implementation (`whoosh_simple.py`)
- **Whoosh-powered indexing** with Japanese preprocessing
- **Industry-standard TF-IDF scoring**
- **Multi-field search** capabilities
- **High-performance binary index**
- **Scalable for large datasets**

### 2. Search Service Layer
- **`search_service.py`** - Custom implementation service
- **`search_service_whoosh.py`** - Whoosh implementation service
- **Query processing** with timing and error handling
- **Unified API** for both implementations

### 3. Flask Web Interface
- **Main page** (`/`) - Clean search interface
- **Results page** (`/search`) - Search results with scores
- **REST API** (`/api/search`, `/api/add_document`)
- **Bootstrap styling** with Japanese UI

### 4. Japanese Text Processing
- **Tokenization**: Extracts 名詞 (nouns), 動詞 (verbs), 形容詞 (adjectives), 副詞 (adverbs)
- **Stop word filtering**: Removes common particles
- **Query processing**: Handles phrases, title searches

## Installation

### Option 1: Using uv (Recommended)

1. **Create and activate virtual environment**:
   ```bash
   uv venv
   source .venv/bin/activate  # Linux/Mac
   # or on Windows: .venv\Scripts\activate
   ```

2. **Install dependencies**:
   ```bash
   uv pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   uv run python run.py
   ```

### Option 2: Direct uv execution (No activation needed)

```bash
# Install dependencies and run directly
uv run --with-requirements requirements.txt python run.py

# Or run tests
uv run --with-requirements requirements.txt python test_search_engine.py
```

4. **Access the web interface**:
   Open http://127.0.0.1:5000 in your browser

## Usage

### Web Interface

1. **Main Search Page** (`/`)
   - Enter Japanese search terms
   - Choose search type (all content or title only)
   - Set result limit (10, 20, or 50)

2. **Search Results** (`/search`)
   - View results with relevance scores
   - Click titles to visit original URLs
   - See search statistics and timing

### REST API

All API endpoints are prefixed with `/api/` and return JSON responses.

#### Search Documents
```bash
GET /api/search?q=検索語&limit=10&type=auto
```

#### Add Single Document
```bash
POST /api/add_document
Content-Type: application/json

{
    "id": "doc1",
    "title": "文書のタイトル",
    "content": "文書の内容...",
    "url": "https://example.com/doc1"
}
```

#### Add Multiple Documents (Batch)
```bash
POST /api/add_documents
Content-Type: application/json

{
    "documents": [
        {
            "id": "doc1",
            "title": "文書1のタイトル",
            "content": "文書1の内容...",
            "url": "https://example.com/doc1"
        },
        {
            "id": "doc2", 
            "title": "文書2のタイトル",
            "content": "文書2の内容...",
            "url": "https://example.com/doc2"
        }
    ]
}
```

#### Get Statistics
```bash
GET /api/stats
```

#### Clear Search Index
```bash
POST /api/clear_index
```

#### Optimize Search Index
```bash
POST /api/optimize_index
```

## How It Works

### 1. Document Indexing
```python
# Add documents via API or batch
search_service.add_document(id, title, content, url)
```

### 2. Search Process
1. User enters Japanese query
2. Query is tokenized by Janome
3. Tokens are matched against inverted index
4. TF-IDF scores are calculated for relevance
5. Results are sorted and returned with snippets

### 3. Japanese Tokenization
```python
# Example tokenization
text = "機械学習の基礎"
tokens = ["機械", "学習", "基礎"]  # Extracted nouns
```

## Features

✅ **Japanese tokenization** with proper part-of-speech filtering  
✅ **TF-IDF relevance scoring** for quality results  
✅ **Title-only search** with `title:` prefix  
✅ **Phrase search** with quotes  
✅ **Web interface** with clean Japanese UI  
✅ **REST API** for programmatic access  
✅ **JSON persistence** for data storage  
✅ **Search statistics** and timing  

## Search Tips

- **Basic search**: `機械学習` - searches all content
- **Title search**: `title:Python` - searches only in titles  
- **Phrase search**: `"データ分析"` - exact phrase matching
- **Multiple terms**: `Flask Django` - finds documents with both terms

## Testing

All test files are organized in the `tests/` directory. Run any test script to see example functionality:

```bash
# Main search engine test
uv run python tests/test_search_engine.py

# Test Whoosh implementation  
uv run python tests/test_whoosh_simple.py

# Test API routes
uv run python tests/test_api_routes.py

# Test tokenization behavior
uv run python tests/test_tokenization_behavior.py

# Compare both implementations
uv run python tests/compare_implementations.py
```

This will:
1. Add sample Japanese documents
2. Test various search queries
3. Display results with scores
4. Show search statistics

## Technical Details

### TF-IDF Scoring
- **Term Frequency (TF)**: How often a term appears in a document
- **Inverse Document Frequency (IDF)**: How rare a term is across all documents
- **Score**: TF × IDF for relevance ranking

### Japanese Text Processing
- Uses Janome tokenizer for morphological analysis
- Filters by part-of-speech (名詞, 動詞, 形容詞, 副詞)
- Removes common stop words and particles
- Handles both hiragana and katakana

### Data Storage
- Documents stored in JSON format
- Inverted index for fast term lookups
- Persistent storage in `data/search_index.json`

## Frontend Development

For frontend developers who want to integrate with this search engine backend:

📚 **[Frontend API Documentation](./FRONTEND_API_DOCS.md)** - Complete guide covering:
- All backend API endpoints and parameters
- Authentication system integration
- Search functionality with Japanese text processing
- Prefecture filtering and metadata handling
- Form structures and client-side validation
- Performance considerations and best practices

The documentation provides everything needed to build a custom frontend or integrate the search engine into existing applications.

## Dependencies

- **Flask**: Web framework
- **Janome**: Japanese tokenization  
- **Whoosh**: Full-text search library (optional)
- **Bootstrap**: UI styling
- **uv**: Fast Python package manager

## Future Enhancements

- [ ] Add fuzzy search capabilities
- [ ] Implement document highlighting
- [ ] Add search history
- [ ] Support for document uploads
- [ ] Advanced search operators
- [ ] Search result pagination