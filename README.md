# Japanese Search Engine

A Flask-based search engine designed specifically for Japanese text processing using Janome tokenization and TF-IDF scoring.

## Project Overview

This search engine provides full-text search capabilities for Japanese documents with a clean web interface and REST API. It uses Janome for Japanese tokenization and implements TF-IDF scoring for relevance ranking.

## Project Structure

```
search_engine/
├── app/                          # Flask application package
│   ├── __init__.py              # App factory with template/static config
│   ├── routes/                  # URL routes and endpoints
│   │   ├── __init__.py
│   │   └── main.py             # Main routes (/, /search, /api/*)
│   ├── services/               # Core search logic
│   │   ├── simple_search.py    # Japanese search engine with TF-IDF
│   │   ├── query_processor.py  # Query parsing and processing
│   │   ├── search_service.py   # Main search service layer
│   │   ├── whoosh_indexer.py   # Original Whoosh implementation
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
├── requirements.txt           # Python dependencies
├── run.py                     # Application entry point
├── test_search_engine.py      # Test script
└── README.md                  # This documentation
```

## Key Components

### 1. Core Search Engine (`simple_search.py`)
- **Japanese tokenization** using Janome (MeCab alternative)
- **TF-IDF scoring** for relevance ranking
- **Inverted index** for fast lookups
- **JSON persistence** for data storage

### 2. Search Service Layer (`search_service.py`)
- **Query processing** with timing
- **Search type handling** (content vs title)
- **Error handling** and statistics
- **API wrapper** for the search engine

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

1. **Create virtual environment**:
   ```bash
   uv venv
   source .venv/bin/activate  # Linux/Mac
   ```

2. **Install dependencies**:
   ```bash
   uv pip install -r requirements.txt
   ```

3. **Run the application**:
   ```bash
   python run.py
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

#### Add Document
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

#### Search Documents
```bash
GET /api/search?q=検索語&limit=10&type=auto
```

#### Get Statistics
```bash
GET /api/stats
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

Run the test script to see example searches:

```bash
python test_search_engine.py
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

## Dependencies

- **Flask**: Web framework
- **Janome**: Japanese tokenization
- **Bootstrap**: UI styling
- **JSON**: Data persistence

## Future Enhancements

- [ ] Add fuzzy search capabilities
- [ ] Implement document highlighting
- [ ] Add search history
- [ ] Support for document uploads
- [ ] Advanced search operators
- [ ] Search result pagination