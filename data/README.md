# Sample Data for Japanese Company Search Engine

This directory contains sample data for testing and development of the Japanese company search engine.

## Files

### `sample_companies.json`
Comprehensive test dataset containing **25 companies** across Japan:

- **7 Tokyo companies**: IT, AI, startups, fintech, logistics
- **4 Osaka companies**: Software, maritime tech, medical systems  
- **4 Fukuoka companies**: Mobile apps, tourism, logistics, defense
- **4 Aichi companies**: Manufacturing, analytics, environment, smart factory
- **2 Kanagawa companies**: Cloud infrastructure, sustainability 
- **1 each**: Kyoto (AI), Hokkaido (mobile), Sendai (fintech), Hiroshima (games)

### `whoosh_index/` (Generated)
Whoosh search index files generated from the sample data. These files are included in git to enable testing across different environments without requiring data reload.

## Company Categories Covered

The sample data includes diverse technology companies to test various search scenarios:

### By Technology Focus
- **AI/Machine Learning**: 4 companies
- **Software Development**: 6 companies  
- **Mobile Apps**: 3 companies
- **IoT/Hardware**: 3 companies
- **Healthcare/Medical**: 2 companies
- **Manufacturing/Industry**: 3 companies
- **Finance/Fintech**: 2 companies
- **Gaming/Entertainment**: 1 company
- **Sustainability/Environment**: 1 company

### By Prefecture
- **tokyo**: 7 companies (28%)
- **osaka**: 4 companies (16%)
- **fukuoka**: 4 companies (16%) 
- **aichi**: 4 companies (16%)
- **kanagawa**: 2 companies (8%)
- **Others**: 4 companies (16%)

## Loading Sample Data

### Option 1: Using the loader script (Recommended)
```bash
# Load all sample data into search index
uv run load_sample_data.py
```

### Option 2: Manual loading via API
```python
from app.services.search_service import SearchService
import json

search_service = SearchService()
with open('data/sample_companies.json', 'r', encoding='utf-8') as f:
    companies = json.load(f)
    
search_service.clear_index()
search_service.add_documents_batch(companies)
```

## Testing Scenarios

The sample data enables comprehensive testing of:

### 1. **Japanese Text Search**
- **Keywords**: Python, Java, React, Vue.js, AI, IoT
- **Japanese terms**: 機械学習, 開発, システム, 管理, 分析
- **Mixed queries**: "Python 開発", "AI システム"

### 2. **Prefecture Filtering**
```bash
# Test prefecture filters
tokyo companies: 7 results
osaka companies: 4 results  
fukuoka companies: 4 results
aichi companies: 4 results
```

### 3. **Search Types**
- **All content**: Searches both company names and descriptions
- **Title only**: Searches only company names
- **Phrase search**: "機械学習", "クラウドサービス"

### 4. **Advanced Features**
- **Multi-keyword search**: "Python 機械学習"
- **Combined filtering**: "開発" + prefecture filter
- **Score-based ranking**: Relevance scoring verification

## Sample Search Queries

Try these queries to test different features:

```bash
# Technology searches
Python          # 3 results - Python development companies
AI              # 3 results - AI/ML companies  
機械学習         # 3 results - Machine learning companies
IoT             # 3 results - IoT companies

# Industry searches  
医療            # 3 results - Medical/healthcare companies
製造業          # 3 results - Manufacturing companies
金融            # 2 results - Financial/fintech companies

# Prefecture + keyword searches
開発 + tokyo    # Development companies in Tokyo
システム + osaka # System companies in Osaka  
アプリ + fukuoka # App companies in Fukuoka
```

## Data Structure

Each company record contains:

```json
{
  "id": "company_001",
  "title": "Company Name in Japanese",
  "content": "Detailed description for search indexing (not displayed)",
  "introduction": "Short company intro for display",
  "url": "https://company-website.co.jp", 
  "prefecture": "tokyo"
}
```

## Index Statistics

After loading sample data:
- **Total documents**: 25 companies
- **Index size**: ~2-3MB (with full Japanese tokenization)
- **Search performance**: Sub-100ms average response time
- **Prefecture coverage**: 9 different prefectures

## Usage in Different Environments

The included Whoosh index files allow immediate testing without data setup:

1. **Development**: Index files included, ready to search
2. **CI/CD**: Automated tests can run against sample data
3. **Demo/Staging**: Consistent dataset across deployments
4. **Local testing**: No additional setup required

## Updating Sample Data

To add more companies or modify existing data:

1. Edit `sample_companies.json`
2. Run `uv run load_sample_data.py` to rebuild index
3. Commit both JSON and index files to git

## Notes

- All company data is fictional but realistic
- URLs are example domains (non-functional)
- Prefecture values match the frontend dropdown options
- Japanese text includes proper business terminology
- Content is optimized for search relevance testing