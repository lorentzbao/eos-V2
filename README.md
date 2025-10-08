# EOS - Japanese Enterprise Search Engine

Modern Flask-based search engine for Japanese companies with intelligent grouping, modular tokenization, and advanced filtering.

---

## 🚀 Quick Start

**Prerequisites:** Python 3.8+ and [uv package manager](https://docs.astral.sh/uv/getting-started/installation/)

```bash
# 1. Clone and setup
git clone https://github.com/lorentzbao/eos-V2.git
cd eos-V2
uv sync

# 2. Start the server
uv run python run.py

# 3. Open browser
# → http://127.0.0.1:5000
```

**Login:** Enter any username (e.g., "demo") to access the search interface.

**Sample Search:** Try searching for "Python 開発" or "AI" to see results.

---

## 📋 Key Features

- **Enterprise Search** - Japanese company search with intelligent URL grouping
- **Modular Tokenization** - Pluggable tokenizer architecture (Janome/MeCab) with easy switching
- **Flexible File Resolution** - Configurable root paths for HTML files with automatic fallback
- **Multi-Index Architecture** - Prefecture-based search routing with separate indexes
- **Advanced Filtering** - Filter by prefecture, city, customer status (白地/契約/過去)
- **Real-time Suggestions** - Google-style dropdown with popular search terms
- **Search Analytics** - Track user searches, popular keywords, and rankings
- **CSV Export** - Download search results in enterprise format
- **OR Search Logic** - Multiple keywords return results with ANY matching terms
- **Hydra Configuration** - Flexible configuration management system

---

## 📚 Documentation

### 👥 For Users
- **[Quick Start Guide](#-quick-start)** - Get started in 2 minutes
- **[User Guide](./docs/guides/TROUBLESHOOTING.md)** - Common issues and solutions

### 💻 For Developers
- **[Frontend Development Guide](./docs/development/FRONTEND_DEVELOPMENT.md)** - Complete frontend setup
- **[API Reference](./docs/api/API_REFERENCE.md)** - Complete API documentation with examples
- **[Web Design Guide](./docs/api/WEBDESIGN.md)** - UI/UX design guidelines
- **[Architecture Guide](./docs/guides/ARCHITECTURE.md)** - Technical architecture overview

### 🔧 For Administrators
- **[Configuration Guide](./CONFIGURATION.md)** - Hydra configuration system
- **[Data Management Guide](./docs/data/SCRIPTS_README.md)** - Index management and utilities
- **[Deployment Guide](./docs/guides/DEPLOYMENT.md)** - Production deployment
- **[Tokenization Guide](./docs/data/TOKENIZED_FORMAT.md)** - Two-step tokenization workflow

### 🤖 For AI Assistants
- **[Claude AI Guide](./docs/development/CLAUDE.md)** - Best practices and project guidance

### 📖 Complete Documentation Index
- **[Documentation Hub](./docs/README.md)** - All documentation organized by category

---

## 🏗️ Technology Stack

- **Backend:** Flask + Whoosh (Japanese full-text search) + Modular Tokenizers (Janome/MeCab)
- **Frontend:** Bootstrap 5 + Vanilla JavaScript (no jQuery dependency)
- **Data Processing:** Pandas + BeautifulSoup4 for HTML content extraction
- **Configuration:** Hydra for flexible configuration management
- **Tokenization:** Abstract tokenizer layer with pluggable backends

---

## 🔗 Quick Links

### Common Tasks
- **Run the server:** `uv run python run.py`
- **Tokenize data:** `uv run python scripts/tokenize_csv.py --config-name json_companies`
- **Create index:** `uv run python scripts/create_index.py --tokenized-dir data/tokenized/`
- **Check index stats:** `uv run python scripts/index_info.py`

### Configuration
- **Switch tokenizer:** `uv run python scripts/tokenize_csv.py tokenizer.type=mecab`
- **Set root paths:** `uv run python scripts/tokenize_csv.py input.primary_root_path=/mnt/e/data`
- **Override settings:** `uv run python run.py app.debug=false app.host=0.0.0.0`

### Documentation
- **API Examples:** [API Reference](./docs/api/API_REFERENCE.md)
- **Troubleshooting:** [Troubleshooting Guide](./docs/guides/TROUBLESHOOTING.md)
- **Data Processing:** [Scripts Guide](./docs/data/SCRIPTS_README.md)

---

## 🤝 Contributing

We welcome contributions! See [CONTRIBUTING.md](./CONTRIBUTING.md) for guidelines.

**Development Process:**
1. Fork the repository
2. Create a feature branch: `git checkout -b feature/your-feature`
3. Make changes following coding standards
4. Add tests for new functionality
5. Submit a pull request

---

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

## 🆘 Support

### Getting Help
- **GitHub Issues:** [Report bugs or request features](https://github.com/lorentzbao/eos-V2/issues)
- **Documentation:** Check our [comprehensive guides](./docs/README.md)
- **Discussions:** Use GitHub Discussions for questions

### Reporting Issues
When reporting issues, please include:
- Operating system and Python version
- Steps to reproduce the problem
- Error messages and logs
- Sample data (if applicable)

### Contact
- **Repository:** https://github.com/lorentzbao/eos-V2
- **Issues:** https://github.com/lorentzbao/eos-V2/issues

---

**Last Updated:** 2025-10-08 | **Version:** 2.0
