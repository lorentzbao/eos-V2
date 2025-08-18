# EOS - Japanese Enterprise Search Engine

A modern Flask-based search engine for Japanese companies with intelligent company grouping, user authentication, CSV exports, and advanced Japanese text processing.

## Quick Start

```bash
# Install and run with uv
uv run python run.py

# Open browser
http://127.0.0.1:5000
```

## Features

✅ **Company Grouping** - Python-side intelligent grouping of multiple URLs per company  
✅ **Japanese Search** - Janome tokenization with full-width/half-width normalization  
✅ **CSV Export** - Download search results with company-focused structure  
✅ **User Authentication** - Simple username-based login system  
✅ **Search History** - Track and view past searches with normalized query consistency  
✅ **Search Rankings** - Real-time popular keyword tracking with Japanese text normalization  
✅ **Smart Suggestions** - Google-style dropdown with popular search terms  
✅ **Metadata Filtering** - Filter companies by prefecture (Tokyo, Osaka, etc.)  
✅ **Client-side Pagination** - Instant navigation through company cards  
✅ **LRU Cache** - Built-in search result caching for instant repeat queries  
✅ **Modern UI** - Clean, responsive interface with clear company/URL hierarchy  
✅ **Comprehensive Data** - 100+ URL records across 47 companies and prefectures  

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
2. **Search**: Enter Japanese keywords (e.g., "Python 開発", "AI", "研究　開発")  
3. **Suggestions**: See popular search terms as you type in Google-style dropdown
4. **Filter**: Select prefecture to narrow results
5. **Browse**: Navigate through company cards with grouped URLs
6. **Export**: Download CSV results with company information and match terms
7. **History**: View your search history (normalized queries for consistency)
8. **Rankings**: Check trending keywords on the rankings page (🏆 button)

## Search Features

- **Company-grouped results**: Multiple URLs per company displayed in organized cards
- **Basic search**: `機械学習` - finds all matching content with company grouping
- **Japanese text normalization**: "研究　開発" and "研究 開発" treated identically  
- **Auto-suggestions**: Smart dropdown with popular searches as you type
- **Title search**: Use "タイトルのみ" dropdown option for URL title-only searches
- **Prefecture filter**: Filter by Tokyo, Osaka, Kyoto, etc.
- **Company pagination**: 10 company cards per page with instant navigation
- **Match highlighting**: See which terms matched for each individual URL
- **CSV export**: Download results with company details and matched terms
- **Rankings tracking**: Real-time keyword popularity with normalized text statistics
- **Keyboard navigation**: Use arrow keys to navigate suggestions

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
- `GET /search` - Search with company grouping and pagination
- `GET /api/download-csv` - Export search results as CSV with authentication
- `GET /rankings` - Popular keyword rankings with normalized text
- `POST /api/add_document` - Add company/URL data with metadata
- `GET /history` - User search history with normalized queries

## Technical Stack

- **Backend**: Flask with Whoosh search engine and Python-side company grouping
- **Frontend**: Bootstrap 5 with optimized JavaScript and client-side pagination  
- **Japanese**: Janome tokenizer with full-width/half-width normalization
- **Cache**: Python's built-in LRU cache (128 entries, auto-clearing on data changes)
- **Data**: JSON-based company records with comprehensive metadata fields
- **Export**: CSV streaming with file-based caching for performance
- **Authentication**: Session-based user tracking with query normalization

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

## 📊 Indexing Your Own Data

### CSV Format

To index your own company data, prepare a CSV file with these required columns:

```csv
id,company_number,company_name,company_tel,company_industry,prefecture,url_name,url,content,title
url_001,1010001000001,株式会社東京テクノロジー,03-1234-5678,情報通信業,tokyo,メインサイト,https://tokyo-tech.co.jp,東京を拠点とするIT企業です。Python開発チーム募集中...,株式会社東京テクノロジー - メインサイト
url_002,1010001000001,株式会社東京テクノロジー,03-1234-5678,情報通信業,tokyo,採用情報,https://tokyo-tech.co.jp/careers,Python開発エンジニア募集。機械学習プロジェクト...,株式会社東京テクノロジー - 採用情報
```

**Field Descriptions:**
- `id` - Unique identifier for each URL record
- `company_number` - Company registration number (for grouping)
- `company_name` - Company name in Japanese
- `company_tel` - Company telephone number  
- `company_industry` - Industry category (e.g., 情報通信業)
- `prefecture` - Prefecture code (tokyo, osaka, kyoto, etc.)
- `url_name` - Descriptive name for the URL (e.g., メインサイト, 採用情報)
- `url` - Full URL to the company page
- `content` - Text content to be indexed and searched
- `title` - Display title combining company name and URL name

### Loading CSV Data

```python
# Example script to load CSV data
import csv
import json
from app.services.search_service import SearchService

def load_csv_data(csv_file_path):
    search_service = SearchService()
    companies = []
    
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        for row in reader:
            companies.append(row)
    
    # Clear existing index and load new data
    search_service.clear_index()
    success = search_service.add_documents_batch(companies)
    print(f"Loaded {len(companies)} records successfully: {success}")

# Usage
load_csv_data('your_company_data.csv')
```

**Tips:**
- Use UTF-8 encoding for Japanese text
- Each row represents one URL for a company
- Multiple URLs can share the same `company_number` for grouping
- `content` field is searchable, `title` is for display
- Prefecture codes: tokyo, osaka, kyoto, aichi, kanagawa, fukuoka, hokkaido, etc.

The search engine is ready to use with sample company data. Add your own data via CSV loading or API endpoints.