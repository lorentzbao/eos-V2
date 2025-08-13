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
// Template receives this data
{
  query: "Python",
  search_type: "auto", 
  prefecture: "tokyo",
  limit: 10,
  results: [
    {
      id: "company_020",
      title: "秋葉原IoT研究所",
      content: "秋葉原のIoT研究所。エッジAI・5G・産業用IoTデバイス開発。Python/C++でのファームウェア開発...",
      url: "https://akihabara-iot.lab",
      score: 1.95,
      matched_terms: ["python"]
    },
    {
      id: "company_005", 
      title: "Tokyo AI Solutions",
      content: "AI・機械学習コンサルティング。Python/TensorFlow専門チーム...",
      url: "https://tokyo-ai-solutions.com",
      score: 1.87,
      matched_terms: ["python"]
    }
  ],
  total_found: 3,
  search_time: 0.156,
  username: "john_doe"
}
```

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

## 🏠 Navigation

```http
GET /           # Home page (search form)
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

### 1. Search Form Template

```html
<form action="/search" method="GET">
  <!-- Search input -->
  <input type="text" name="q" required 
         placeholder="検索キーワードを入力...">

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

  <button type="submit">検索</button>
</form>
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

### JavaScript Pagination *(Already Implemented)*
- Results automatically paginated at 10 items per page
- No server requests needed for page navigation
- Smart pagination with numbered buttons + ellipsis

### Japanese Search *(Already Implemented)*  
- Proper Japanese tokenization with Janome
- OR-based search (multiple keywords expand results)
- Prefecture metadata filtering

### Search History *(Already Implemented)*
- Efficient reverse file reading (scales to GB+ logs)
- User-specific search tracking
- Scalable pagination (8 recent, up to 100 total)

---

## 🎯 What You Need to Do

1. **Style the existing templates** in `/templates/`
2. **Customize CSS** in `/static/css/style.css`  
3. **Add JavaScript features** if needed
4. **Test with sample data** (25+ companies included)

### Sample Searches to Try:
- `Python` - Python development companies
- `AI` - Artificial intelligence companies  
- `フィンテック` - Fintech companies
- `ゲーム` - Gaming companies

---

## 🛠️ Development

```bash
# Backend runs with auto-reload
uv run python run.py

# Load sample data
uv run python load_sample_data.py

# Access at http://127.0.0.1:5000
```

**That's it!** The backend handles authentication, search, pagination, and history. You just need to style the frontend.