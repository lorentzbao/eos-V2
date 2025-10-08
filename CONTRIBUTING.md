# Contributing to EOS

Thank you for your interest in contributing to EOS Japanese Enterprise Search Engine!

---

## 🤝 How to Contribute

### Development Process

1. **Fork the repository**
   ```bash
   # Click "Fork" on GitHub
   git clone https://github.com/YOUR_USERNAME/eos-V2.git
   cd eos-V2
   ```

2. **Create a feature branch**
   ```bash
   git checkout -b feature/your-feature-name
   # Or for bug fixes
   git checkout -b fix/bug-description
   ```

3. **Make your changes**
   - Follow coding standards (see below)
   - Add tests for new functionality
   - Update documentation

4. **Test your changes**
   ```bash
   # Run tests
   uv run pytest

   # Test with sample data
   uv run python run.py
   ```

5. **Commit with clear messages**
   ```bash
   git add .
   git commit -m "Add: brief description of changes"
   ```

6. **Push and create Pull Request**
   ```bash
   git push origin feature/your-feature-name
   # Then create PR on GitHub
   ```

---

## 📝 Coding Standards

### Python Code Style

**Follow PEP 8:**
- Use 4 spaces for indentation (not tabs)
- Maximum line length: 100 characters
- Use descriptive variable names
- Add docstrings to functions and classes

**Example:**
```python
def search_companies(query: str, prefecture: str, limit: int = 10) -> List[Dict]:
    """
    Search for companies matching the query.
    
    Args:
        query: Search query string
        prefecture: Prefecture code (e.g., 'tokyo')
        limit: Maximum number of results
        
    Returns:
        List of company dictionaries with search results
    """
    # Implementation here
    pass
```

### Type Hints

Use type hints for function parameters and return values:
```python
from typing import List, Dict, Optional

def process_data(data: Dict[str, str], limit: Optional[int] = None) -> List[str]:
    # Implementation
    pass
```

### Imports

Order imports as follows:
```python
# 1. Standard library
import os
import sys
from typing import List, Dict

# 2. Third-party packages
import flask
from whoosh import index

# 3. Local modules
from app.services import SearchService
```

### Japanese Text Handling

- Always use UTF-8 encoding
- Test with actual Japanese characters
- Handle both hiragana, katakana, and kanji
- Use `encoding='utf-8'` explicitly when reading/writing files

---

## 🧪 Testing Guidelines

### Write Tests for New Features

```python
# tests/test_new_feature.py
import pytest
from app.services.your_service import YourService

def test_new_feature():
    """Test description"""
    service = YourService()
    result = service.new_feature("test")
    assert result == expected_value
```

### Run Tests

```bash
# Run all tests
uv run pytest

# Run specific test file
uv run pytest tests/test_search_engine.py

# Run with verbose output
uv run pytest -v

# Run with coverage
uv run pytest --cov=app
```

### Test Japanese Text

Always include Japanese text in tests:
```python
def test_japanese_search():
    query = "Python 開発"
    results = search_service.search(query)
    assert len(results) > 0
```

---

## 📚 Documentation

### Update Documentation

When adding new features:
1. Update relevant `.md` files in `docs/`
2. Add examples to `docs/api/API_REFERENCE.md` if API changes
3. Update `README.md` if necessary
4. Add entry to `TODO.md` and mark as completed

### Documentation Style

- Use clear, concise language
- Provide code examples
- Include expected output
- Add troubleshooting tips

---

## 🎯 Areas for Contribution

### High Priority

- **UI/UX Improvements**
  - Mobile responsiveness
  - Accessibility (ARIA labels, keyboard navigation)
  - Loading states and user feedback

- **Search Enhancements**
  - Advanced query syntax
  - Fuzzy search for typos
  - Search result ranking improvements

- **Performance Optimizations**
  - Redis caching layer
  - Database for search logs
  - Query optimization

### Medium Priority

- **Additional Features**
  - Search filters (date range, employee count)
  - Saved searches
  - User preferences
  - Email alerts

- **Testing**
  - End-to-end tests
  - Performance benchmarks
  - Load testing

### Low Priority

- **Nice-to-Have**
  - Dark mode
  - Multi-language support
  - Advanced analytics dashboard

---

## 🐛 Reporting Bugs

### Before Reporting

1. Check [existing issues](https://github.com/lorentzbao/eos-V2/issues)
2. Try the latest version
3. Check [troubleshooting guide](./docs/guides/TROUBLESHOOTING.md)

### Bug Report Template

```markdown
**Describe the bug**
A clear description of what the bug is.

**To Reproduce**
Steps to reproduce:
1. Go to '...'
2. Click on '...'
3. Scroll down to '...'
4. See error

**Expected behavior**
What you expected to happen.

**Environment:**
- OS: [e.g., Ubuntu 22.04]
- Python version: [e.g., 3.11.0]
- Browser: [e.g., Chrome 120]

**Error messages:**
```
Paste error messages here
```

**Additional context**
Any other relevant information.
```

---

## 💡 Feature Requests

### Suggesting Features

1. Check if feature already exists or is planned
2. Open a GitHub Issue with:
   - Clear description of the feature
   - Use cases and benefits
   - Possible implementation approach
   - Examples from other projects (if applicable)

---

## 🔍 Code Review Process

### What We Look For

- **Correctness:** Does it work as intended?
- **Code quality:** Is it readable and maintainable?
- **Tests:** Are there adequate tests?
- **Documentation:** Is it documented?
- **Performance:** Does it introduce performance issues?
- **Security:** Does it introduce security vulnerabilities?

### Review Timeline

- Initial review: Within 1-3 days
- Follow-up: Within 1-2 days
- Merge: After approval from maintainers

---

## 🎓 Learning Resources

### Japanese NLP
- [Janome Documentation](https://mocobeta.github.io/janome/en/)
- [MeCab Documentation](https://taku910.github.io/mecab/)
- [Whoosh Documentation](https://whoosh.readthedocs.io/)

### Flask
- [Flask Documentation](https://flask.palletsprojects.com/)
- [Flask Mega-Tutorial](https://blog.miguelgrinberg.com/post/the-flask-mega-tutorial-part-i-hello-world)

### Testing
- [Pytest Documentation](https://docs.pytest.org/)
- [Testing Flask Applications](https://flask.palletsprojects.com/en/latest/testing/)

---

## 📞 Getting Help

- **Documentation:** Check [docs/](./docs/)
- **GitHub Discussions:** Ask questions
- **GitHub Issues:** Report bugs
- **Email:** Contact project maintainers

---

## 📜 Code of Conduct

### Our Standards

- Be respectful and inclusive
- Welcome newcomers
- Provide constructive feedback
- Focus on what is best for the community

### Unacceptable Behavior

- Harassment or discriminatory language
- Trolling or insulting comments
- Personal or political attacks
- Publishing others' private information

---

**Thank you for contributing to EOS!** 🎉

Your contributions help make this project better for everyone.

**Last Updated:** 2025-10-08
