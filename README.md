# EOS - Japanese Enterprise Search Engine

Modern Flask-based search engine for Japanese companies with intelligent grouping, advanced text processing, and HTML content extraction.

## 🚀 Quick Start

```bash
# Install dependencies
uv add flask janome whoosh beautifulsoup4 pandas hydra-core

# Start with default configuration
uv run python run.py

# Or with custom configuration
uv run python run.py index.dir=data/custom/index

# Open browser
http://127.0.0.1:5000
```

**Default Login:** Enter any username to start

## 📋 Key Features

- **Enterprise Search** - Japanese company search with intelligent URL grouping
- **HTML Content Extraction** - Extract and tokenize content from HTML files with configurable length limits
- **Flexible Input Sources** - Support for CSV files and JSON folder structures
- **Two-Step Tokenization** - Separate tokenization and indexing for preprocessing flexibility
- **Customer Filtering** - Filter by customer status (白地/既存) and prefecture
- **Auto-suggestions** - Google-style dropdown with popular search terms
- **Search Analytics** - Track user searches, popular keywords, and rankings
- **CSV Export** - Download search results in enterprise format
- **OR Search Logic** - Multiple keywords return results with ANY matching terms
- **Hydra Configuration** - Flexible configuration management system

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

## 🛠️ Data Processing & Index Management

### **Two-Step Tokenization Workflow (Recommended)**

```bash
# Step 1: Tokenize data with HTML content extraction using Hydra configuration
uv run python scripts/tokenize_csv.py --config-name tokenize_json

# Step 2: Create index from tokenized data
python scripts/create_index.py --tokenized-dir data/test_json_companies/tokenized

# Alternative: Process CSV files
uv run python scripts/tokenize_csv.py --config-name tokenize_csv
python scripts/create_index.py --tokenized-dir data/sample_companies/tokenized
```

### **Configuration-Based Input Sources**

```bash
# JSON folder with company data and HTML content (using preset)
uv run python scripts/tokenize_csv.py --config-name tokenize_json

# CSV file processing (using preset)
uv run python scripts/tokenize_csv.py --config-name tokenize_csv

# Override specific settings
uv run python scripts/tokenize_csv.py --config-name tokenize_json processing.batch_size=1000 processing.max_content_length=5000

# Select specific DataFrame columns
uv run python scripts/tokenize_csv.py --config-name tokenize processing.extra_columns=[cust_status,revenue]
```

### **Index Management**

For detailed documentation, see: **[scripts/README.md](./scripts/README.md)**

```bash
# Add more data to existing index
python scripts/add_to_index.py data/new_companies.csv

# Check index health and performance
python scripts/index_info.py

# Delete index
python scripts/delete_index.py
```

## 🏗️ Technical Stack

- **Backend:** Flask + Whoosh (Japanese full-text search) + Janome (tokenization)
- **HTML Processing:** BeautifulSoup4 for content extraction from HTML files
- **Data Processing:** Pandas for DataFrame operations and data merging
- **Configuration:** Hydra for flexible configuration management
- **Frontend:** Bootstrap 5 + JavaScript (pagination, auto-suggestions)
- **Data Formats:** CSV files and JSON folder structures with URL-based record generation
- **Performance:** LRU cache + file-based CSV export caching + O(1) dictionary lookups for data merging

## 📚 Documentation

- **[Configuration Guide](./CONFIGURATION.md)** - Hydra configuration system and deployment options
- **[API Reference](./FRONTEND_API_DOCS.md)** - Complete frontend API documentation
- **[Scripts Documentation](./scripts/README.md)** - Index management, tokenization, and utility scripts
- **[Tokenized Format Specification](./scripts/TOKENIZED_FORMAT.md)** - Two-step tokenization workflow format
- **[Sample Data Guide](./data/README.md)** - Testing data and development examples

## 🔧 Development

```bash
# Install all dependencies
uv add flask janome whoosh beautifulsoup4 pandas hydra-core

# Run development server with default config
uv run python run.py

# Run with custom configuration
uv run python run.py app.debug=false index.dir=data/production/index

# Process sample data
python scripts/tokenize_csv.py --json-folder data/test_json_companies
python scripts/create_index.py --tokenized-dir data/test_json_companies/tokenized
```

### **Configuration Management**

The project uses Hydra for flexible configuration:

```bash
# Default configuration (conf/config.yaml)
uv run python run.py

# Override specific settings
uv run python run.py app.debug=false index.dir=data/custom/

# Use different config file
uv run python run.py --config-path custom/path --config-name custom_config
```

**Sample Data:** Includes JSON company data with HTML content files for testing HTML extraction functionality

