# EOS - Japanese Enterprise Search Engine

Modern Flask-based search engine for Japanese companies with intelligent grouping, advanced text processing, and HTML content extraction.

## 📋 Table of Contents

### **For End Users**
- [🚀 Quick Start](#-quick-start) - Try the search engine in 2 minutes
- [📋 Key Features](#-key-features) - What EOS can do
- [📖 How to Use](#-how-to-use) - Search, filter, and export features
- [🔧 Troubleshooting](#-troubleshooting) - Common issues and solutions

### **For Developers**
- [🛠️ Development Setup](#️-development-setup) - Local development environment
- [📚 Developer Documentation](#-developer-documentation) - Detailed guides for frontend and backend
- [🏗️ Technical Architecture](#️-technical-architecture) - Stack and design overview

### **For Administrators**
- [🚀 Deployment](#-deployment) - Production deployment guide
- [📊 Data Management](#-data-management) - Index and data processing
- [⚙️ Configuration](#️-configuration) - Advanced settings

### **Project Information**
- [🤝 Contributing](#-contributing) - How to contribute to EOS
- [📄 License](#-license) - Usage terms and conditions
- [🆘 Support](#-support) - Getting help and reporting issues

## 🚀 Quick Start

**Prerequisites:** Python 3.8+ and [uv package manager](https://docs.astral.sh/uv/getting-started/installation/)

```bash
# 1. Clone and setup
git clone https://github.com/lorentzbao/eos-V2.git
cd eos-V2
uv sync

# 2. Start the server
uv run python run.py

# 3. Open browser and start searching
# → http://127.0.0.1:5000
```

**Login:** Enter any username (e.g., "demo") to access the search interface.

**Sample Search:** Try searching for "Python 開発" or "AI" to see the search in action.

## 📋 Key Features

- **Enterprise Search** - Japanese company search with intelligent URL grouping
- **Modular Tokenization** - Pluggable tokenizer architecture (Janome/MeCab) with easy switching
- **Flexible File Resolution** - Configurable root paths for HTML files with automatic fallback
- **HTML Content Extraction** - Extract and tokenize content from HTML files with configurable length limits
- **Flexible Input Sources** - Support for CSV files and JSON folder structures
- **Two-Step Tokenization** - Separate tokenization and indexing for preprocessing flexibility
- **Customer Filtering** - Filter by customer status (白地/既存) and prefecture
- **Auto-suggestions** - Google-style dropdown with popular search terms
- **Search Analytics** - Track user searches, popular keywords, and rankings
- **CSV Export** - Download search results in enterprise format
- **OR Search Logic** - Multiple keywords return results with ANY matching terms
- **Hydra Configuration** - Flexible configuration management system

## 📖 How to Use

### **Search Interface**
1. **Enter search terms** in Japanese or English (e.g., "Python 開発", "AI")
2. **Use filters** to narrow results:
   - **Prefecture:** Tokyo, Osaka, or other locations
   - **Customer Status:** 白地 (prospects), 契約 (contract), or 過去 (past)
   - **Results per page:** 10, 20, or 50 companies
3. **Review results** grouped by company with multiple URLs
4. **Export to CSV** for further analysis

### **Search Tips**
- **OR Logic:** "Python 開発" finds companies with Python OR 開発
- **Multiple Keywords:** Use space-separated terms for broader results
- **Japanese Support:** Full Japanese text search with intelligent tokenization
- **Auto-suggestions:** Start typing to see popular search terms

### **Data Export**
Click the "CSV Download" button on search results to export company data including:
- Company details (name, address, status)
- Contact information and URLs
- Business classification and employee count
- Matched search terms and relevance scores

📚 **For developers:** Complete API documentation at [app/API_REFERENCE.md](./app/API_REFERENCE.md)

## 🔧 Troubleshooting

### **Common Issues**

**Server won't start:**
```bash
# Check if uv is installed
uv --version

# Install dependencies if missing
uv sync

# Check port availability
lsof -i :5000  # Kill process if port is busy
```

**Empty search results:**
- Ensure sample data is loaded (see [Data Management](#-data-management))
- Check if index exists in `data/` directory
- Try basic queries like "AI" or "Python" first

**Permission errors:**
```bash
# Fix file permissions
chmod -R 755 data/
chmod +x scripts/*.py
```

**Japanese text display issues:**
- Ensure UTF-8 encoding in browser
- Check terminal/IDE supports Japanese characters

### **Getting Help**
- Check [Issues on GitHub](https://github.com/lorentzbao/eos-V2/issues)
- Review logs in terminal for error details
- See [Support](#-support) section for contact information

---

## 🛠️ Development Setup

### **Prerequisites**
- Python 3.8 or higher
- [uv package manager](https://docs.astral.sh/uv/getting-started/installation/)
- Git for version control

### **Quick Development Setup**
```bash
# Clone and setup (see detailed setup in documentation links below)
git clone https://github.com/lorentzbao/eos-V2.git
cd eos-V2 && uv sync

# Run development server
uv run python run.py

# Access at http://127.0.0.1:5000
```

**Frontend developers:** See [Frontend Development Guide](./FRONTEND_DEVELOPMENT.md) for complete setup
**Backend developers:** See [Configuration Guide](./CONFIGURATION.md) for advanced settings

### **Development with Sample Data**
```bash
# Process and index sample data
uv run python scripts/tokenize_csv.py --config-name json_companies
uv run python scripts/create_index.py --tokenized-dir data/test_json_companies/tokenized

# Start server with indexed data
uv run python run.py
```

**Note:** For detailed data processing, index management, and production deployment, see [Data Management](#-data-management) section.

## 📚 Developer Documentation

### **Frontend Development**
- **[🚀 Frontend Development Guide](./FRONTEND_DEVELOPMENT.md)** - Complete setup guide
  - Windows/Linux installation instructions
  - Git workflow with frontend-dev branch
  - Project folder structure and UI/UX files
  - Jinja2 templating and JavaScript/AJAX integration

### **API Integration**
- **[🔗 API Reference](./app/API_REFERENCE.md)** - Complete API documentation
  - Search APIs with filters and pagination
  - CSV export with enterprise data fields
  - Authentication and session management
  - JavaScript examples for all endpoints

### **Backend Development**
- **[Configuration Guide](./CONFIGURATION.md)** - Hydra configuration system
- **[Scripts Documentation](./scripts/README.md)** - Index management and utilities
- **[Data Processing Guide](./scripts/TOKENIZED_FORMAT.md)** - Two-step tokenization workflow
- **[Sample Data Guide](./data/README.md)** - Testing data and examples

## 🏗️ Technical Architecture

### **Core Technologies**
- **Backend:** Flask + Whoosh (Japanese full-text search) + Modular Tokenizers (Janome/MeCab)
- **Frontend:** Bootstrap 5 + Vanilla JavaScript (no jQuery dependency)
- **Data Processing:** Pandas + BeautifulSoup4 for HTML content extraction
- **Configuration:** Hydra for flexible configuration management
- **Tokenization:** Abstract tokenizer layer with pluggable backends

### **Performance Features**
- **Caching:** LRU cache + file-based CSV export caching
- **Search:** O(1) dictionary lookups for data merging
- **Japanese Support:** UTF-8 encoding with proper tokenization
- **Scalability:** Multi-index support for prefecture-based search
- **Flexible I/O:** Configurable root paths with automatic fallback for different environments

### **Tokenization Architecture**

EOS uses a modular tokenizer architecture that allows easy switching between different Japanese tokenizers:

- **Abstract Base Layer:** `BaseTokenizer` defines the common interface
- **Token Dataclass:** Unified representation across all tokenizers
- **Pluggable Backends:**
  - **Janome** - Pure Python, easy installation (default)
  - **MeCab** - C++ based, faster performance (optional)
  - Easy to add new tokenizers (Sudachi, Kuromoji, etc.)
- **Factory Pattern:** Auto-detection with graceful fallback
- **Configuration-based:** Switch tokenizers via config without code changes

**File Structure:**
```
app/services/tokenizers/
├── __init__.py           # Package exports
├── base_tokenizer.py     # Abstract base class + Token dataclass
├── janome_tokenizer.py   # Janome adapter
├── mecab_tokenizer.py    # MeCab adapter
└── factory.py            # get_tokenizer() factory function
```

---

## 🚀 Deployment

### **Production Deployment**
```bash
# Quick production setup
export FLASK_ENV=production
uv run python run.py app.debug=false app.host=0.0.0.0 app.port=80
```

📚 **Complete deployment guide:** [CONFIGURATION.md](./CONFIGURATION.md)

### **Environment Variables**
- `FLASK_SECRET_KEY` - Secret key for sessions
- `INDEX_DIR` - Path to search index directory
- `DEBUG` - Enable/disable debug mode

## 📊 Data Management

### **Index Creation Workflow**
```bash
# Step 1: Tokenize your data
uv run python scripts/tokenize_csv.py --config-name json_companies

# Step 2: Create search index
uv run python scripts/create_index.py --tokenized-dir data/tokenized/

# Step 3: Verify index
uv run python scripts/index_info.py
```

### **Advanced Tokenization Options**
```bash
# Use specific tokenizer backend
uv run python scripts/tokenize_csv.py tokenizer.type=janome
uv run python scripts/tokenize_csv.py tokenizer.type=mecab

# Configure root paths for HTML files (useful for different mount points)
uv run python scripts/tokenize_csv.py \
  input.json_folder=data/raw/tokyo \
  input.primary_root_path=/mnt/e/data \
  input.secondary_root_path=/home/user/data

# Combine options
uv run python scripts/tokenize_csv.py \
  --config-name json_companies \
  tokenizer.type=janome \
  input.primary_root_path=/mnt/e/data
```

### **Adding New Data**
```bash
# Add CSV data to existing index
uv run python scripts/add_to_index.py data/new_companies.csv

# Rebuild entire index
uv run python scripts/delete_index.py
uv run python scripts/create_index.py --tokenized-dir data/tokenized/
```

### **Index Management**
```bash
# Check index statistics
uv run python scripts/index_info.py

# Backup index
cp -r data/indexes/ backups/indexes-$(date +%Y%m%d)

# Restore from backup
cp -r backups/indexes-20240101/ data/indexes/
```

**For detailed documentation:** See **[scripts/README.md](./scripts/README.md)**

## ⚙️ Configuration

EOS uses Hydra for flexible configuration management. Basic usage:

```bash
# Default configuration
uv run python run.py

# Override settings
uv run python run.py app.debug=false index.dir=data/production/

# Tokenizer configuration
uv run python run.py tokenizer.type=janome
```

**Configuration files:**
- `conf/config.yaml` - Main application config with tokenizer settings
- `conf/json_companies.yaml` - JSON processing preset
- `conf/tokenize.yaml` - Tokenization defaults with root path configuration

**Key Configuration Options:**
- `tokenizer.type` - Choose tokenizer: `janome`, `mecab`, or `null` for auto-detect
- `input.primary_root_path` - Primary root path for HTML file resolution
- `input.secondary_root_path` - Fallback root path if primary fails
- `processing.batch_size` - Records per batch for tokenization
- `processing.use_multiprocessing` - Enable parallel processing

📚 **Complete guide:** [CONFIGURATION.md](./CONFIGURATION.md)

---

## 🤝 Contributing

We welcome contributions to EOS! Here's how to get started:

### **Development Process**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make your changes following our coding standards
4. Add tests for new functionality
5. Submit a pull request

### **Coding Standards**
- Follow PEP 8 for Python code
- Use type hints where appropriate
- Add docstrings to functions and classes
- Test Japanese text handling thoroughly

### **Areas for Contribution**
- UI/UX improvements
- Search algorithm enhancements
- Additional data format support
- Performance optimizations
- Documentation improvements

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## 🆘 Support

### **Getting Help**
- **GitHub Issues:** [Report bugs or request features](https://github.com/lorentzbao/eos-V2/issues)
- **Documentation:** Check our comprehensive guides in the repo
- **Discussions:** Use GitHub Discussions for questions

### **Reporting Issues**
When reporting issues, please include:
- Operating system and Python version
- Steps to reproduce the problem
- Error messages and logs
- Sample data (if applicable)

### **Contact**
- **Repository:** https://github.com/lorentzbao/eos-V2
- **Issues:** https://github.com/lorentzbao/eos-V2/issues

