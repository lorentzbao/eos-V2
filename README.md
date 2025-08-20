# EOS - Japanese Enterprise Search Engine

Modern Flask-based search engine for Japanese companies with intelligent grouping and advanced text processing.

## 🚀 Quick Start

```bash
# Install and run
uv run python run.py

# Load sample data
python scripts/create_index.py data/sample_companies.csv

# Open browser
http://127.0.0.1:5000
```

**Default Login:** Enter any username to start

## 📋 Key Features

- **Enterprise Search** - Japanese company search with intelligent URL grouping
- **Customer Filtering** - Filter by customer status (白地/既存) and prefecture
- **Auto-suggestions** - Google-style dropdown with popular search terms
- **Search Analytics** - Track user searches, popular keywords, and rankings
- **CSV Export** - Download search results in enterprise format
- **OR Search Logic** - Multiple keywords return results with ANY matching terms

## 📖 Usage

### **Basic Search**
```bash
# Search Japanese companies
Query: "Python 開発"     # OR logic: Python OR 開発
Query: "AI 人工知能"     # Returns companies with AI OR 人工知能
Query: "研究　開発"      # Normalized automatically
```

### **Advanced Filtering**
- **Prefecture:** Filter by location (tokyo, osaka, etc.)
- **Customer Status:** Filter by 白地 (prospects) or 既存 (existing)
- **Results Limit:** 10, 20, or 50 results per page

### **CSV Export**
```bash
# Download search results
http://127.0.0.1:5000/api/download-csv?q=Python&prefecture=tokyo&cust_status=白地
```

## 🛠️ Index Management

For creating, deleting, and managing search indexes, see: **[scripts/README.md](./scripts/README.md)**

**Quick Commands:**
```bash
# Create index from CSV
python scripts/create_index.py data/sample_companies.csv

# Add more data to existing index
python scripts/add_to_index.py data/new_companies.csv

# Check index health and performance
python scripts/index_info.py

# Delete index
python scripts/delete_index.py
```

## 🏗️ Technical Stack

- **Backend:** Flask + Whoosh (Japanese full-text search) + Janome (tokenization)
- **Frontend:** Bootstrap 5 + JavaScript (pagination, auto-suggestions)
- **Data:** Enterprise CSV format with JCN-based company grouping
- **Performance:** LRU cache + file-based CSV export caching

## 📚 Documentation

- **[API Reference](./FRONTEND_API_DOCS.md)** - Complete API documentation
- **[Index Management](./scripts/README.md)** - CSV import/export, index utilities

## 🔧 Development

```bash
# Install dependencies  
pip install Flask==3.0.0 Janome==0.5.0 Whoosh==2.7.4

# Run development server
uv run python run.py

# Load sample data
python scripts/create_index.py data/sample_companies.csv
```

**Sample Data:** 25 records across 11 companies with diverse industries (AI/ML, fintech, healthcare, agriculture)

