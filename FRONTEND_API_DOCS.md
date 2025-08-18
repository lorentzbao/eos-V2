# Frontend API Guide
**EOS - Japanese Enterprise Search Engine**

Quick reference for frontend developers to integrate with the EOS backend.

---

## 🚀 Quick Start

```bash
# Start backend
uv run python run.py

# Backend runs on http://127.0.0.1:5000
```

## 🔐 Authentication

Simple username-based sessions. All search endpoints require login.

## 🔤 Japanese Text Normalization

**Important:** The backend automatically normalizes Japanese text queries:
- Full-width spaces (　) → Half-width spaces ( )
- Queries like "研究　開発" and "研究 開発" are treated identically
- This ensures consistent search history and ranking tracking
- Normalization applies to search queries, history, and CSV exports

```http
# Login
POST /login
Content-Type: application/x-www-form-urlencoded

username=john_doe
```

**Sample Response:**
```http
HTTP/1.1 302 Found
Location: /
Set-Cookie: session=eyJ1c2VybmFtZSI6ImpvaG5fZG9lIn0...; HttpOnly; Path=/
```

```http
# Logout  
GET /logout
```

**Sample Response:**
```http
HTTP/1.1 302 Found  
Location: /login
Set-Cookie: session=; Expires=Thu, 01 Jan 1970 00:00:00 GMT; Path=/
```

---

## 🔍 Main Search API

**Endpoint:** `GET /search`

**Parameters:**
```javascript
{
  q: "search query",        // Required, non-empty
  type: "auto",             // "auto" | "title" (default: "auto") 
  limit: 10,                // 10 | 20 | 50 (default: 10)
  prefecture: "tokyo"       // Optional prefecture filter
}
```

**Examples:**
```http
GET /search?q=Python&limit=20
GET /search?q=機械学習&type=title&prefecture=osaka
GET /search?q=AI開発&prefecture=tokyo
```

**Response:** HTML page with search results + pagination JavaScript

**Sample Output Structure:**
```javascript
// Template receives company-grouped data
{
  query: "Python",
  search_type: "auto", 
  prefecture: "tokyo",
  limit: 10,
  grouped_results: [
    {
      company_name: "株式会社東京テクノロジー",
      company_number: "1010001000001",
      company_tel: "03-1234-5678",
      company_industry: "情報通信業",
      prefecture: "tokyo",
      urls: [
        {
          url: "https://tokyo-tech.co.jp",
          url_name: "メインサイト",
          content: "東京を拠点とするIT企業です。Python、Java、React開発チームを募集中...",
          matched_terms: ["python"],
          score: 1.95,
          id: "url_001"
        },
        {
          url: "https://tokyo-tech.co.jp/careers",
          url_name: "採用情報",
          content: "Python開発エンジニア募集。機械学習プロジェクトにも参加可能...",
          matched_terms: ["python"],
          score: 1.87,
          id: "url_002"
        }
      ]
    }
  ],
  total_found: 5,
  total_companies: 2,
  search_time: 0.156,
  username: "john_doe"
}
```

---

## 📥 CSV Export API

**Endpoint:** `GET /api/download-csv`

**Authentication:** Required (user must be logged in)

**Parameters:**
```javascript
{
  q: "search query",        // Required, same as search
  type: "auto",             // Optional: "auto" (default) or "title"  
  prefecture: "tokyo"       // Optional: prefecture filter
}
```

**Examples:**
```http
GET /api/download-csv?q=Python&prefecture=tokyo
GET /api/download-csv?q=機械学習&type=title
```

**Response:** CSV file download with UTF-8 BOM encoding

**CSV Structure:**
```csv
Company_Number,Company_Name,Company_Tel,Company_Industry,Prefecture,URL_Name,URL,Content,Matched_Terms,ID
1010001000001,株式会社東京テクノロジー,03-1234-5678,情報通信業,tokyo,メインサイト,https://tokyo-tech.co.jp,東京を拠点とするIT企業です...,python,url_001
1010001000001,株式会社東京テクノロジー,03-1234-5678,情報通信業,tokyo,採用情報,https://tokyo-tech.co.jp/careers,Python開発エンジニア募集...,python,url_002
```

**Features:**
- File-based caching for performance (repeated queries serve cached files instantly)
- Company-focused structure (company information repeated for each URL)
- Sorted by company_number for consistent grouping
- Matched terms separated by `|` for multiple matches
- Content truncated to 500 characters
- UTF-8 BOM for Excel compatibility

---

## 📊 Search History

**Endpoint:** `GET /history`

**Parameters:**
```javascript
{
  show_all: true  // false: 8 entries, true: up to 100 entries
}
```

**Examples:**
```http
GET /history              // Latest 8 searches
GET /history?show_all=true // Up to 100 searches  
```

**Response:** HTML page with search history table

**Sample Output Structure:**
```javascript
// Template receives this data
{
  searches: [
    {
      timestamp: "2024-01-15T10:30:45.123456",
      query: "Python開発",
      search_type: "auto",
      prefecture: "tokyo",
      results_count: 24,
      search_time: 0.156
    },
    {
      timestamp: "2024-01-15T10:25:12.789012", 
      query: "機械学習",
      search_type: "title",
      prefecture: "",
      results_count: 8,
      search_time: 0.089
    },
    {
      timestamp: "2024-01-15T10:20:33.456789",
      query: "フィンテック",
      search_type: "auto", 
      prefecture: "osaka",
      results_count: 12,
      search_time: 0.134
    }
  ],
  username: "john_doe",
  show_all: false,
  limit: 8,
  total_searches: 156
}
```

---

## 🏆 Search Rankings & Suggestions

### Rankings Page

**Endpoint:** `GET /rankings`

**Response:** HTML page showing popular keyword rankings with statistics

**Sample Output Structure:**
```javascript
// Template receives this data
{
  queries: [
    {
      query: "python",
      count: 12,
      percentage: 35.3
    },
    {
      query: "機械学習", 
      count: 8,
      percentage: 23.5
    },
    {
      query: "ai",
      count: 6, 
      percentage: 17.6
    }
  ],
  stats: {
    total_queries: 34,
    unique_queries: 15,
    top_query: ["python", 12]
  },
  username: "john_doe"
}
```

### Smart Search Suggestions

**Auto-completion dropdowns** are embedded in search forms:

**Features:**
- Instant suggestions from popular search keywords
- Google-style dropdown with keyboard navigation
- No API calls needed (data embedded in templates)
- Real-time filtering as user types

**Implementation:**
```javascript
// Popular queries data is embedded in each page
window.popularQueries = [
  {"query": "python", "count": 12},
  {"query": "機械学習", "count": 8},
  {"query": "ai", "count": 6}
];

// Suggestions appear instantly on:
// - Focus on search input
// - Typing in search input  
// - Clicking search input
```

---

## 🏠 Navigation

```http
GET /           # Home page (search form with suggestions)
GET /search     # Search results page (with suggestions)  
GET /rankings   # Popular keyword rankings page
GET /history    # User search history
GET /login      # Login form  
GET /logout     # Destroys session, redirects to login
```

**Sample Outputs:**

**Home Page (`GET /`):**
```http
HTTP/1.1 200 OK
Content-Type: text/html

<!-- Returns index.html template with: -->
{
  username: "john_doe"
}
```

**Login Page (`GET /login`):**  
```http
HTTP/1.1 200 OK
Content-Type: text/html

<!-- Returns login.html template with login form -->
<!-- If POST with username, redirects to / with session -->
```

---

## 📝 Frontend Integration

### 1. Search Form Template with Auto-suggestions

```html
<form action="/search" method="GET">
  <div class="input-group position-relative">
    <!-- Search input with suggestions -->
    <input type="text" 
           id="searchInput"
           name="q" 
           required
           autocomplete="off"
           placeholder="検索キーワードを入力...">
    <button type="submit">検索</button>
    
    <!-- Auto-suggestions dropdown -->
    <div id="searchSuggestions" class="suggestions-dropdown" style="display: none;">
      <div class="suggestions-header">
        <small class="text-muted">🏆 人気の検索キーワード</small>
      </div>
      <div id="suggestionsList">
        <!-- Populated by JavaScript -->
      </div>
    </div>
  </div>

  <!-- Search type -->
  <select name="type">
    <option value="auto">すべて検索</option>
    <option value="title">タイトルのみ</option>
  </select>

  <!-- Prefecture filter -->
  <select name="prefecture">
    <option value="">すべての地域</option>
    <option value="tokyo">東京都</option>
    <option value="osaka">大阪府</option>
    <option value="kyoto">京都府</option>
    <option value="aichi">愛知県</option>
    <option value="kanagawa">神奈川県</option>
    <option value="fukuoka">福岡県</option>
  </select>

  <!-- Results limit -->
  <select name="limit">
    <option value="10">10件</option>
    <option value="20">20件</option>
    <option value="50">50件</option>
  </select>
</form>

<!-- Embed popular queries data -->
<script>
window.popularQueries = {{ popular_queries | tojson }};
</script>
```

### 2. Empty Search Prevention

```javascript
// Prevent empty submissions (Google-style)
document.querySelector('form').addEventListener('submit', function(e) {
  const query = document.querySelector('input[name="q"]').value.trim();
  if (!query) {
    e.preventDefault();
    // Show validation feedback
    document.querySelector('input[name="q"]').classList.add('is-invalid');
  }
});
```

### 3. State Preservation

```html
<!-- Keep user selections after search -->
<select name="type">
  <option value="auto" {% if search_type == 'auto' %}selected{% endif %}>
    すべて検索
  </option>
  <option value="title" {% if search_type == 'title' %}selected{% endif %}>
    タイトルのみ  
  </option>
</select>
```

---

## 🎨 Template Data

### Search Results Page

The `/search` endpoint provides these template variables:

```javascript
{
  // Search info
  query: "Python",              // Original query
  search_type: "auto",          // Search type used
  prefecture: "tokyo",          // Prefecture filter  
  limit: 10,                    // Results limit
  
  // Results
  results: [                    // Array of search results
    {
      id: "doc1",               // Document ID
      title: "Python開発会社",   // Document title
      content: "Pythonで...",    // Document introduction
      url: "https://...",       // Document URL
      score: 7.5,               // Relevance score (0-10)
      matched_terms: ["Python"] // Highlighted terms
    }
  ],
  total_found: 24,              // Total results count
  search_time: 0.15,            // Search time in seconds
  
  // User info  
  username: "john_doe"          // Current user
}
```

### History Page

The `/history` endpoint provides:

```javascript
{
  searches: [                   // User's search history
    {
      timestamp: "2023-...",    // When searched
      query: "Python",          // What they searched
      search_type: "auto",      // Search type
      prefecture: "tokyo",      // Prefecture filter (if any)
      results_count: 24,        // Results found
      search_time: 0.15         // How long it took
    }
  ],
  username: "john_doe",         // Current user
  show_all: false,              // Pagination state
  total_searches: 156           // Total user searches
}
```

---

## ✨ Built-in Features

### Company Grouping *(Already Implemented)*
- Python-side intelligent grouping of multiple URLs per company
- Clean company cards showing company info with nested URL items  
- Optimized performance without client-side processing overhead
- CSV exports maintain company structure with flattened URL data

### JavaScript Pagination *(Already Implemented)*
- Company cards paginated at 10 companies per page (not individual URLs)
- No server requests needed for page navigation
- Smart pagination with numbered buttons + ellipsis
- Cached pagination calculations for better performance

### Japanese Search *(Already Implemented)*  
- Proper Japanese tokenization with Janome
- Full-width/half-width space normalization (研究　開発 = 研究 開発)
- OR-based search (multiple keywords expand results)
- Prefecture metadata filtering with company-aware results

### Search History *(Already Implemented)*
- Efficient reverse file reading (scales to GB+ logs)
- User-specific search tracking with normalized queries
- Consistent history (full-width and half-width spaces treated identically)
- Scalable pagination (8 recent, up to 100 total)

### CSV Export *(Already Implemented)*  
- Authenticated download endpoint with file-based caching
- Company-focused structure with repeated company info per URL
- UTF-8 BOM encoding for Excel compatibility
- Sorted by company_number for consistent grouping

### Search Rankings & Suggestions *(Already Implemented)*
- Real-time keyword popularity tracking with text normalization
- In-memory rankings with startup initialization from existing logs
- Google-style auto-suggestions with keyboard navigation
- Rankings page with medal badges and progress bars
- Zero-latency suggestions (data embedded in templates)

---

## 🎯 What You Need to Do

1. **Style the existing templates** in `/templates/`
2. **Customize CSS** in `/static/css/style.css`  
3. **Add JavaScript features** if needed
4. **Test with sample data** (100+ URL records across 47 companies included)

### Sample Searches to Try:
- `Python` - Python development companies (shows company grouping)
- `AI` or `人工知能` - Artificial intelligence companies  
- `フィンテック` - Fintech companies
- `ゲーム` - Gaming companies
- `研究　開発` or `研究 開発` - R&D companies (demonstrates text normalization)

---

## 🛠️ Development

```bash
# Backend runs with auto-reload
uv run python run.py

# Load sample data
uv run python load_sample_data.py

# Access at http://127.0.0.1:5000
```

**That's it!** The backend handles authentication, search with company grouping, CSV exports, Japanese text normalization, pagination, and history. You just need to style the frontend.