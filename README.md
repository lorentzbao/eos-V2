# EOS - Japanese Enterprise Search Engine

Modern Flask-based search engine for Japanese companies with intelligent grouping and advanced text processing.

---

## 🚀 Quick Start

```bash
# Install and run
uv run python run.py

# Open browser
http://127.0.0.1:5000
```

**Default Login:** Enter any username to start

---

## 📋 Services Overview

### **Search Services**
- **Company Search** - Intelligent grouping of multiple URLs per company
- **Japanese Text Processing** - Janome tokenization with normalization  
- **Auto-suggestions** - Google-style dropdown with popular terms
- **Prefecture Filtering** - Location-based company filtering

### **Data Export Services**  
- **CSV Export** - Download search results with company structure
- **File Caching** - Performance optimization for repeated exports
- **UTF-8 BOM Encoding** - Excel-compatible Japanese text

### **User Services**
- **Authentication** - Simple username-based sessions
- **Search History** - Track past searches with query normalization
- **Rankings** - Real-time popular keyword tracking
- **Pagination** - Client-side navigation through company cards

### **Data Management Services**
- **Index Management** - Add/clear/optimize search index
- **Batch Loading** - CSV-based bulk data import
- **LRU Cache** - Built-in result caching (128 entries)
- **Query Logging** - User search tracking with normalization

---

## 🔍 How to Use Each Service

### 1. **Company Search**
```bash
# Access via browser
http://127.0.0.1:5000

# Search Japanese companies
Query: "Python 開発"
Query: "AI 人工知能" 
Query: "研究　開発"  # Normalized automatically
```

**Features:**
- Multiple URLs grouped by company
- Match highlighting for each URL
- Prefecture filtering (Tokyo, Osaka, etc.)
- 10/20/50 results per page

### 2. **CSV Export**
```bash
# Download search results
http://127.0.0.1:5000/api/download-csv?q=Python&prefecture=tokyo
```

**Output Format:**
```csv
Company_Number,Company_Name,Company_Tel,Company_Industry,Prefecture,URL_Name,URL,Content,Matched_Terms,ID
1010001000001,株式会社東京テクノロジー,03-1234-5678,情報通信業,tokyo,メインサイト,https://tokyo-tech.co.jp,東京を拠点とする...,python,url_001
```

### 3. **Search History**
```bash
# View user search logs
http://127.0.0.1:5000/history

# Show all searches
http://127.0.0.1:5000/history?show_all=true
```

**Features:**
- Normalized query consistency ("研究　開発" = "研究 開発")
- Timestamp, search type, results count
- Prefecture filter tracking
- Scalable pagination (8 recent, up to 100 total)

### 4. **Popular Rankings**
```bash
# View trending keywords  
http://127.0.0.1:5000/rankings
```

**Features:**
- Real-time keyword popularity
- Search count and percentage
- Japanese text normalization applied
- Medal badges for top terms

### 5. **Data Management**
```bash
# Add single document
POST /api/add_document
{
  "id": "url_001",
  "company_name": "株式会社テスト",
  "company_number": "1010001000001",
  "content": "テスト用コンテンツ"
}

# Clear index
POST /api/clear_index

# Optimize index  
POST /api/optimize_index
```

### 6. **Batch CSV Loading**
```python
# Load CSV data
import csv
from app.services.search_service import SearchService

def load_csv_data(csv_file_path):
    search_service = SearchService()
    companies = []
    
    with open(csv_file_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        companies = list(reader)
    
    search_service.clear_index()
    success = search_service.add_documents_batch(companies)
    print(f"Loaded {len(companies)} records: {success}")

# Usage
load_csv_data('company_data.csv')
```

---

## 📊 Sample Usage

### **Search Examples**
```bash
# Technology companies
"Python" → Python development companies
"AI" → Artificial intelligence companies  
"フィンテック" → Fintech companies
"ゲーム" → Gaming companies

# With filters
"機械学習" + prefecture:"tokyo" → Tokyo ML companies
"研究 開発" → R&D companies (normalized text)
```

### **CSV Export Examples**
```bash
# All Python companies
/api/download-csv?q=Python

# Tokyo fintech companies
/api/download-csv?q=フィンテック&prefecture=tokyo

# Title-only search export
/api/download-csv?q=AI&type=title
```

---

## 🛠️ Technical Architecture

### **Backend Services**
- **Flask** - Web framework with session management
- **Whoosh** - Full-text search engine with company grouping
- **Janome** - Japanese tokenization and text processing
- **LRU Cache** - Built-in result caching (auto-clearing)

### **Frontend Services**  
- **Bootstrap 5** - Responsive UI framework
- **JavaScript** - Client-side pagination and suggestions
- **Company Cards** - Clean visual hierarchy for grouped results
- **Auto-suggestions** - Google-style dropdown with keyboard navigation

### **Data Services**
- **JSON Records** - Company and URL metadata storage
- **File-based Caching** - CSV export performance optimization  
- **Query Normalization** - Japanese text consistency across services
- **Session Logging** - Per-user search tracking

---

## 📚 Service Documentation

**For Developers:** [Complete API Reference](./FRONTEND_API_DOCS.md)

**Quick API Reference:**
- `GET /search` - HTML search with company grouping
- `GET /api/search` - JSON search API  
- `GET /api/download-csv` - CSV export (authenticated)
- `POST /api/add_document` - Add single record
- `POST /api/add_documents` - Batch add records
- `GET /history` - Search history page
- `GET /rankings` - Popular keywords page

---

## 🔧 Development Setup

```bash
# Install dependencies
pip install Flask==3.0.0 Janome==0.5.0 Whoosh==2.7.4

# Run with auto-reload
uv run python run.py

# Load sample data (100+ records)
uv run python load_sample_data.py

# Access services
http://127.0.0.1:5000
```

## 📊 Custom Data Import

### **CSV Format Specification**

Required columns for company data import:

```csv
id,company_number,company_name,company_tel,company_industry,prefecture,url_name,url,content,title
url_001,1010001000001,株式会社東京テクノロジー,03-1234-5678,情報通信業,tokyo,メインサイト,https://tokyo-tech.co.jp,東京を拠点とするIT企業です...,株式会社東京テクノロジー - メインサイト
```

### **Field Requirements**
- `id` - Unique URL identifier  
- `company_number` - Company registration number (grouping key)
- `company_name` - Japanese company name
- `company_tel` - Contact telephone
- `company_industry` - Industry category  
- `prefecture` - Location code (tokyo, osaka, kyoto, etc.)
- `url_name` - URL description (メインサイト, 採用情報, etc.)
- `url` - Full company page URL
- `content` - Searchable text content
- `title` - Display title (company + URL name)

### **Import Instructions**

1. **Prepare CSV file** with UTF-8 encoding
2. **Multiple URLs per company** using same `company_number` 
3. **Load via Python script** (see Batch CSV Loading above)
4. **Or use API endpoints** for individual records

**Ready to use:** Sample data included (100+ records, 47 companies)