# Frontend Developer API Documentation
## Enterprise Online Search (EOS) Backend Services

This document provides comprehensive information about the backend APIs and services available for frontend integration.

---

## 🏗️ Backend Architecture Overview

The backend is built with **Flask** and provides a complete search engine with user authentication, search logging, and metadata filtering capabilities.

### Core Technologies
- **Search Engine**: Whoosh with Japanese text processing (Janome tokenizer)
- **Database**: File-based JSON logs + Whoosh index
- **Authentication**: Flask sessions
- **API Style**: Traditional server-rendered with RESTful endpoints

---

## 🔐 Authentication System

### Session-Based Authentication
All search endpoints require user authentication via Flask sessions.

**Login Flow:**
```http
POST /login
Content-Type: application/x-www-form-urlencoded

username=john_doe
```

**Response:** Redirects to main search page with session cookie

**Logout:**
```http
GET /logout
```

**Session Check:**
- All protected routes check `session['username']`
- Unauthorized requests redirect to `/login`

---

## 🔍 Search API Endpoints

### 1. Main Search Endpoint

**URL:** `GET /search`

**Description:** Primary search functionality with Japanese text processing and metadata filtering

**Query Parameters:**
```javascript
{
  q: string,           // Search query (required, non-empty)
  type: string,        // Search type: "auto" | "title" (default: "auto")
  limit: number,       // Results limit: 10 | 20 | 50 (default: 10)
  prefecture: string   // Prefecture filter: "tokyo" | "osaka" | etc. (optional)
}
```

**Example Requests:**
```http
GET /search?q=Python&type=auto&limit=10
GET /search?q=機械学習&type=title&prefecture=tokyo
GET /search?q=開発&limit=20&prefecture=osaka
```

**Response Format:**
The endpoint renders `search.html` template with these variables:
```javascript
{
  query: string,              // Original search query
  results: Array<{            // Search results
    id: string,               // Document ID
    title: string,            // Document title
    content: string,          // Document content
    url: string,              // Document URL
    score: number,            // Relevance score (0-10)
    matched_terms: string[]   // Highlighted terms
  }>,
  total_found: number,        // Total results count
  search_time: number,        // Search execution time (seconds)
  processed_query: string,    // Processed query for debugging
  search_type: string,        // Search type used
  prefecture: string,         // Prefecture filter applied
  limit: number,              // Results limit applied
  username: string,           // Current user
  stats: {                    // Index statistics
    total_documents: number
  }
}
```

**Search Types:**
- `"auto"`: Searches in both title and content fields
- `"title"`: Searches only in document titles

**Prefecture Filtering:**
Supported prefecture values:
```javascript
const PREFECTURES = [
  "tokyo",      // 東京都
  "osaka",      // 大阪府  
  "kyoto",      // 京都府
  "aichi",      // 愛知県
  "kanagawa",   // 神奈川県
  "fukuoka",    // 福岡県
  "hokkaido",   // 北海道
  "sendai",     // 宮城県
  "hiroshima"   // 広島県
];
```

### 2. Empty Query Handling
- Empty or whitespace-only queries redirect to `GET /`
- Frontend should prevent empty submissions with JavaScript validation

---

## 📊 Search History API

### Get User Search History

**URL:** `GET /history`

**Description:** Retrieves paginated search history for the current user

**Query Parameters:**
```javascript
{
  show_all: boolean,  // false: show latest 8, true: show up to 100
  limit: number      // Override default limit (internal use)
}
```

**Example Requests:**
```http
GET /history                    // Latest 8 entries
GET /history?show_all=true      // Up to 100 entries
```

**Response Format:**
Renders `history.html` template with:
```javascript
{
  searches: Array<{
    timestamp: string,      // ISO timestamp
    query: string,          // Search query
    search_type: string,    // "auto" | "title"
    prefecture?: string,    // Prefecture filter (if applied)
    results_count: number,  // Number of results found
    search_time: number     // Search duration (seconds)
  }>,
  username: string,         // Current user
  show_all: boolean,        // Current pagination state
  limit: number,            // Current limit
  total_searches: number    // Total user search count
}
```

**Performance Features:**
- Uses reverse file reading for O(entries_needed) performance
- Efficient for large log files (GB+ scale)
- Shows most recent entries first

---

## 🏠 Navigation Endpoints

### 1. Home Page
**URL:** `GET /`
**Description:** Main search interface
**Template:** `index.html`

### 2. Login Page  
**URL:** `GET /login`
**Description:** User authentication form
**Template:** `login.html`

### 3. Logout
**URL:** `GET /logout`  
**Description:** Destroys session and redirects to login

---

## 💾 Document Management (Backend Internal)

### Search Service Architecture

**Core Services:**
```python
# app/services/search_service.py
class SearchService:
    def search(query, limit, search_type, prefecture) -> dict
    def add_document(doc_id, title, content, url, prefecture) -> bool
    def add_documents_batch(documents) -> bool
    def get_stats() -> dict
    def clear_index() -> bool

# app/services/search_logger.py  
class SearchLogger:
    def log_search(username, query, search_type, results_count, search_time, prefecture)
    def get_user_searches(username, limit) -> list
```

**Document Schema:**
```javascript
{
  id: string,           // Unique document ID
  title: string,        // Document title
  content: string,      // Document content  
  url: string,          // Document URL (optional)
  prefecture: string    // Prefecture metadata (optional)
}
```

---

## 🎨 Frontend Integration Guide

### 1. Form Structure

**Main Search Form:**
```html
<form action="/search" method="GET">
  <input type="text" name="q" required>
  
  <select name="type">
    <option value="auto">すべて検索</option>
    <option value="title">タイトルのみ</option>
  </select>
  
  <select name="prefecture">
    <option value="">すべての地域</option>
    <option value="tokyo">東京都</option>
    <option value="osaka">大阪府</option>
    <!-- ... more prefectures -->
  </select>
  
  <select name="limit">
    <option value="10">10件</option>
    <option value="20">20件</option>
    <option value="50">50件</option>
  </select>
  
  <button type="submit">検索</button>
</form>
```

### 2. Client-Side Validation

**Empty Search Prevention (Google-style):**
```javascript
document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('input[name="q"]');
    
    function validateAndSubmit(form) {
        const query = searchInput.value.trim();
        if (query === '') {
            // Show validation feedback
            searchInput.classList.add('is-invalid');
            searchInput.focus();
            setTimeout(() => {
                searchInput.classList.remove('is-invalid');
            }, 1500);
            return false;
        }
        return true;
    }
    
    // Handle form submission
    const searchForm = searchInput.closest('form');
    searchForm.addEventListener('submit', function(e) {
        if (!validateAndSubmit(this)) {
            e.preventDefault();
        }
    });
});
```

### 3. State Persistence

**Maintaining Form State:**
```html
<!-- Preserve user selections in results page -->
<select name="type">
  <option value="auto" {% if search_type == 'auto' %}selected{% endif %}>すべて検索</option>
  <option value="title" {% if search_type == 'title' %}selected{% endif %}>タイトルのみ</option>
</select>

<select name="prefecture">
  <option value="" {% if not prefecture %}selected{% endif %}>すべての地域</option>
  <option value="tokyo" {% if prefecture == 'tokyo' %}selected{% endif %}>東京都</option>
  <!-- ... -->
</select>
```

---

## 📱 Responsive Design Requirements

### CSS Framework
- **Bootstrap 5.1.3** is loaded via CDN
- Custom styles in `/static/css/style.css`
- Brand colors: Primary `#001871`, Secondary `#0A2C8A`

### Key UI Components

**Search Results:**
```html
<div class="result-item mb-4 p-3 border rounded">
  <h5 class="result-title">
    <a href="{{ result.url }}" target="_blank">{{ result.title }}</a>
    <small class="text-muted">(スコア: {{ result.score }})</small>
  </h5>
  <p class="result-content text-muted">{{ result.content }}</p>
  
  <!-- Matched terms badges -->
  <div class="matched-terms-sidebar">
    {% for term in result.matched_terms %}
    <span class="badge bg-primary">{{ term }}</span>
    {% endfor %}
  </div>
</div>
```

**History Table:**
```html
<table class="table table-hover">
  <thead>
    <tr>
      <th>検索時刻</th>
      <th>検索クエリ</th>
      <th>検索タイプ</th>
      <th>地域フィルター</th>
      <th>結果数</th>
      <th>検索時間</th>
      <th>アクション</th>
    </tr>
  </thead>
  <!-- ... -->
</table>
```

---

## 🚀 Performance Considerations

### Search Performance
- **Whoosh index** provides sub-100ms search times
- **Prefecture filtering** uses efficient KEYWORD field filters
- **Japanese tokenization** with Janome for accurate results

### History Performance  
- **Reverse file reading** scales to GB+ log files
- **Default 8 entries** for fast page loads
- **Lazy loading** for full history (100 entries max)

### Scalability
- **File-based storage** suitable for medium-scale deployments
- **Session-based auth** for simplicity
- **Client-side validation** reduces server load

---

## 🛠️ Development Setup

### Running the Backend
```bash
# Install dependencies
uv sync

# Run Flask development server
uv run python app.py

# Access at http://localhost:5000
```

### API Testing
```bash
# Test search endpoint
curl "http://localhost:5000/search?q=Python&type=auto&limit=5"

# Test with prefecture filter
curl "http://localhost:5000/search?q=開発&prefecture=tokyo"
```

---

## 🔍 Search Query Processing

### Japanese Text Processing
- **Janome tokenizer** for Japanese morphological analysis
- **Stop word removal** (だ, である, です, ます, etc.)
- **OR-based search** - multiple keywords expand results

### Query Examples
```javascript
// Simple search
"Python" → matches documents containing "Python"

// Multiple keywords (OR logic)  
"Python 開発" → matches docs with "Python" OR "開発"

// Phrase search
'"機械学習"' → matches exact phrase "機械学習"

// Title-only search
"title:Python" → searches only in document titles
```

### Search Scoring
- **Whoosh BM25F algorithm** for relevance scoring
- **Title matches** get higher scores than content matches
- **Multiple term matches** increase relevance score
- **Scores typically range** from 0-10

---

## 📋 Error Handling

### Common Error Scenarios

**Empty Search:**
- Client-side validation prevents submission
- Backend redirects empty queries to home page

**Session Expired:**
- All protected routes redirect to `/login`
- Frontend should handle authentication redirects

**Search Errors:**
- Backend returns empty results on search failures
- Errors logged server-side for debugging

### Status Codes
- **200**: Successful requests (includes empty results)
- **302**: Redirects (auth, empty queries)
- **404**: Route not found
- **500**: Server errors (rare with error handling)

---

## 🎯 Next Steps for Frontend Developer

1. **Review the existing templates** in `/templates/` for current implementation
2. **Check `/static/css/style.css`** for current styling patterns
3. **Test all endpoints** with different parameter combinations
4. **Implement responsive design improvements** if needed
5. **Add any additional client-side features** (autocomplete, etc.)

### Questions or Issues?
- Check the Flask routes in `/app/routes/main.py`
- Review service implementations in `/app/services/`
- Test with the existing frontend at http://localhost:5000

---

*Generated for EOS v1.0 - Japanese Enterprise Search Engine*