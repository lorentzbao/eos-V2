# Troubleshooting Guide

Common issues and solutions for the EOS Japanese Enterprise Search Engine.

---

## 🚨 Common Issues

### Server Won't Start

**Symptoms:** Server fails to start or crashes immediately

**Solutions:**
```bash
# Check if uv is installed
uv --version

# Install dependencies if missing
uv sync

# Check port availability
lsof -i :5000  # Kill process if port is busy
# Or run on different port
uv run python run.py app.port=8000
```

**Check Python version:**
```bash
python --version  # Should be 3.8 or higher
```

---

### Empty Search Results

**Symptoms:** Search returns no results even with simple queries

**Possible Causes:**
1. Index not created or empty
2. Prefecture not selected (required for multi-index)
3. Query syntax issues

**Solutions:**
```bash
# Check if index exists and has data
uv run python scripts/index_info.py

# If empty, create index from sample data
uv run python scripts/tokenize_csv.py --config-name json_companies
uv run python scripts/create_index.py --tokenized-dir data/tokenized/tokyo

# Try basic queries first
# - Simple keywords: "AI", "Python"
# - Make sure prefecture is selected
```

---

### Permission Errors

**Symptoms:** Cannot read/write files, permission denied errors

**Solutions:**
```bash
# Fix file permissions
chmod -R 755 data/
chmod +x scripts/*.py

# Check directory ownership
ls -la data/

# If using WSL, check mount permissions
# Add to /etc/wsl.conf:
# [automount]
# options = "metadata"
```

---

### Japanese Text Display Issues

**Symptoms:** Japanese characters show as ?, boxes, or garbled text

**Solutions:**
1. **Browser:** Ensure UTF-8 encoding
   - Chrome: Settings → Advanced → Languages → UTF-8
   - Firefox: View → Text Encoding → UTF-8

2. **Terminal:** Set terminal encoding to UTF-8
   ```bash
   export LANG=en_US.UTF-8
   export LC_ALL=en_US.UTF-8
   ```

3. **CSV Files:** Use UTF-8 with BOM for Excel compatibility
   - Already handled by the application
   - Open CSV files with "UTF-8" encoding in Excel

---

### Tokenization Errors

**Symptoms:** Tokenization fails or produces unexpected results

**Solutions:**
```bash
# Check tokenizer installation
uv run python -c "from janome.tokenizer import Tokenizer; print('Janome OK')"

# If MeCab errors occur
uv run python scripts/tokenize_csv.py tokenizer.type=janome

# Check input file encoding
file -i data/input.csv  # Should show charset=utf-8

# Verify JSON structure
python -m json.tool data/raw/tokyo/company.json
```

---

### Index Corruption

**Symptoms:** Search crashes, index errors, inconsistent results

**Solutions:**
```bash
# Backup current index
cp -r data/indexes/tokyo data/indexes/tokyo.backup

# Clear and rebuild index
uv run python scripts/delete_index.py
uv run python scripts/create_index.py --tokenized-dir data/tokenized/tokyo

# If corruption persists, clear tokenized data and start fresh
rm -rf data/tokenized/tokyo
uv run python scripts/tokenize_csv.py input.json_folder=data/raw/tokyo
uv run python scripts/create_index.py --tokenized-dir data/tokenized/tokyo
```

---

### Configuration Issues

**Symptoms:** Config overrides not working, wrong settings loaded

**Solutions:**
```bash
# Verify config file syntax
python -c "from omegaconf import OmegaConf; OmegaConf.load('conf/config.yaml')"

# Check Hydra outputs directory
ls -la outputs/  # Shows recent run configurations

# Use explicit config overrides
uv run python run.py --config-name config tokenizer.type=janome

# Debug config loading
uv run python run.py --cfg job  # Shows resolved configuration
```

---

### Memory Issues

**Symptoms:** Out of memory errors during tokenization or indexing

**Solutions:**
```bash
# Reduce batch size for tokenization
uv run python scripts/tokenize_csv.py processing.batch_size=100

# Process data in smaller chunks
# Split large JSON folders into multiple runs

# Monitor memory usage
top -p $(pgrep -f "python.*tokenize")

# For very large datasets
# - Disable multiprocessing: processing.use_multiprocessing=false
# - Reduce concurrent I/O: processing.max_concurrent_io=4
```

---

### Session/Login Issues

**Symptoms:** Constantly redirected to login, session not persisting

**Solutions:**
```bash
# Check secret key is set
grep secret_key conf/config.yaml

# Set a proper secret key in production
# Don't use the default "your-secret-key-here"

# Clear browser cookies
# - Chrome: Settings → Privacy → Clear browsing data
# - Firefox: Preferences → Privacy → Clear Data

# Check if session directory exists
ls -la flask_session/  # If using file-based sessions
```

---

## 🔍 Debugging Tips

### Enable Debug Mode
```bash
# Run with debug enabled
uv run python run.py app.debug=true

# Check detailed error traces in terminal
```

### Check Logs
```bash
# Application logs (if logging configured)
tail -f logs/eos.log

# Check Hydra output logs
ls -la outputs/$(date +%Y-%m-%d)/
```

### Test Individual Components
```bash
# Test tokenizer
uv run python -c "
from app.services.tokenizers import get_tokenizer
t = get_tokenizer('janome')
print(t.tokenize_and_filter('テスト'))
"

# Test search service
uv run python -c "
from app.services.search_service import SearchService
s = SearchService('data/indexes/tokyo')
print(s.get_document_count())
"
```

---

## 📞 Getting Additional Help

If the issue persists:

1. **Check Documentation:**
   - [Configuration Guide](../../CONFIGURATION.md)
   - [Scripts Guide](../data/SCRIPTS_README.md)
   - [API Reference](../api/API_REFERENCE.md)

2. **Search Existing Issues:**
   - [GitHub Issues](https://github.com/lorentzbao/eos-V2/issues)

3. **Report New Issue:**
   - Include error messages
   - Provide steps to reproduce
   - Mention OS and Python version
   - Attach relevant config files

4. **Community Support:**
   - GitHub Discussions
   - Project maintainers

---

**Last Updated:** 2025-10-08
