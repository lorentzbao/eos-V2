# EOS - Japanese Enterprise Search Engine

A modern Flask-based search engine for Japanese companies with user authentication, search history, and metadata filtering.

## Quick Start

```bash
# Install and run with uv
uv run python run.py

# Open browser
http://127.0.0.1:5000
```

## Features

✅ **Japanese Search** - Janome tokenization with proper Japanese text processing  
✅ **User Authentication** - Simple username-based login system  
✅ **Search History** - Track and view past searches with scalable pagination  
✅ **Metadata Filtering** - Filter companies by prefecture (Tokyo, Osaka, etc.)  
✅ **Client-side Pagination** - Instant navigation through search results  
✅ **Modern UI** - Clean, responsive interface with Bootstrap  
✅ **Sample Data** - 25+ test companies across Japanese prefectures  

## Project Structure

```
eos/
├── app/
│   ├── routes/           # Web routes (main.py, api.py)
│   └── services/         # Search logic (Whoosh-based)
├── templates/            # HTML templates
├── static/              # CSS, JavaScript
├── data/                # Search index and logs
└── requirements.txt
```

## How to Use

1. **Login**: Enter any username to start
2. **Search**: Enter Japanese keywords (e.g., "Python 開発", "AI")  
3. **Filter**: Select prefecture to narrow results
4. **Browse**: Use pagination to navigate through results
5. **History**: View your search history with details

## Search Features

- **Basic search**: `機械学習` - finds all matching content
- **Title search**: Use "タイトルのみ" dropdown option
- **Prefecture filter**: Filter by Tokyo, Osaka, Kyoto, etc.
- **Smart pagination**: 10 results per page with instant navigation
- **Match highlighting**: See which terms matched your query

## Sample Searches

Try these with the included sample data:
- `Python` - finds Python development companies
- `AI` or `人工知能` - artificial intelligence companies  
- `フィンテック` - fintech companies
- `ゲーム` - gaming companies

## API Endpoints

For frontend developers:

📚 **[Complete API Documentation](./FRONTEND_API_DOCS.md)**

Quick reference:
- `GET /search` - Search with pagination
- `POST /api/add_document` - Add company data
- `GET /history` - User search history

## Technical Stack

- **Backend**: Flask with Whoosh search engine
- **Frontend**: Bootstrap 5 with JavaScript pagination  
- **Japanese**: Janome tokenizer for proper text processing
- **Data**: JSON-based persistence with binary search index
- **Authentication**: Session-based user tracking

## Dependencies

```txt
Flask==3.0.0
Janome==0.5.0  
Whoosh==2.7.4
```

## Development

```bash
# Run with auto-reload
uv run python run.py

# Load sample data
uv run python load_sample_data.py
```

The search engine is ready to use with sample company data. Add your own data via the API endpoints or modify `load_sample_data.py`.