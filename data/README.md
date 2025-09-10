# Sample Data

Test data for the Japanese company search engine with HTML content extraction capabilities.

## Files

### **Legacy CSV Data**
**`sample_companies.csv`** - 25 Japanese companies across 9 prefectures covering AI/ML, software, mobile, IoT, healthcare, manufacturing, fintech, and gaming.

### **JSON Company Data with HTML Content**
**`test_json_companies/`** - Modern JSON-based company data with HTML content extraction
- `company_001.json` - 株式会社テックイノベーション (AI/ML company)
- `company_002.json` - 株式会社グリーンテック (Environmental tech company)

**`HTML/2025/Homepage/`** - Sample HTML files for content extraction testing
- `tech_001.html` - Main site for tech company
- `tech_001_services.html` - Services page with AI/ML details  
- `tech_001_about.html` - Company overview and history
- `green_001.html` - Environmental tech company main site
- `green_001_products.html` - Environmental products and solutions

### **Additional Test Data**
**`test_company_info.csv`** - Additional company information for DataFrame merging tests

## Processing Examples

### **Modern JSON Workflow (Recommended)**
```bash
# Process JSON companies with HTML content extraction (using Hydra configuration)
uv run python scripts/tokenize_csv.py --config-name tokenize_json
python scripts/create_index.py --tokenized-dir data/test_json_companies/tokenized

# Test HTML content truncation with override
uv run python scripts/tokenize_csv.py --config-name tokenize_json processing.max_content_length=500

# Select specific DataFrame columns
uv run python scripts/tokenize_csv.py --config-name tokenize_json processing.extra_columns=[cust_status]
```

### **Legacy CSV Processing**
```bash
# Traditional CSV workflow
python scripts/create_index.py data/sample_companies.csv
```

## Data Features

### **JSON Company Structure**
- **Company Information** - JCN, names (Japanese/English), address, industry
- **Homepage Data** - Main domain and sub-domain URLs
- **HTML Content Paths** - References to HTML files for content extraction
- **URL Tags** - Descriptive tags for sub-domain pages

### **HTML Content Extraction**
- **BeautifulSoup Processing** - Clean text extraction from HTML
- **Content Truncation** - Configurable length limits to prevent overwhelming tokenization
- **Japanese Text Processing** - Janome tokenization with POS filtering

## Test Coverage

### **Legacy CSV Data**
**Industries:** AI/ML (4), Software (6), Mobile (3), IoT (3), Healthcare (2), Manufacturing (3), Fintech (2), Gaming (1), Sustainability (1)

**Prefectures:** Tokyo (7), Osaka (4), Fukuoka (4), Aichi (4), Kanagawa (2), Others (4)

### **JSON Test Data**
**Companies:** 2 companies with 5 URL records (main + sub-domains)
- AI/ML Technology Company (Tokyo) - 3 URLs
- Environmental Technology Company (Osaka) - 2 URLs

**HTML Content:** 5 HTML files with realistic Japanese business content

## Test Queries

**Keywords:** Python, AI, 機械学習, 環境技術, データ分析, リサイクル

**Prefecture filters:** tokyo (tech companies), osaka (environmental companies)

**Content-based queries:** "tensorflow pytorch", "廃棄物処理", "人工知能システム"