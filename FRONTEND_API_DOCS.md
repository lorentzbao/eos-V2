# Frontend API Reference
**EOS - Japanese Enterprise Search Engine**

Clean API documentation for frontend developers.

---

## 🚀 Quick Start

```bash
# Start backend
uv run python run.py

# Backend runs on http://127.0.0.1:5000
```

**Authentication:** All endpoints require login via session cookies.

**Japanese Text:** Queries are normalized (full-width spaces → half-width spaces).

---

## 📋 API Overview

### **HTML Pages** (for browser integration)
- `GET /` - Home page with search form
- `GET /search` - Search results with company grouping  
- `GET /login` / `POST /login` - Authentication
- `GET /logout` - Session cleanup
- `GET /history` - User search history
- `GET /rankings` - Popular keywords

### **JSON APIs** (for AJAX/fetch integration)
- `GET /api/search` - Search with JSON response
- `GET /api/download-csv` - CSV export (authenticated)
- `GET /api/stats` - Search engine statistics
- `POST /api/add_document` - Add single record
- `POST /api/add_documents` - Batch add records  
- `POST /api/clear_index` - Clear index
- `POST /api/optimize_index` - Optimize index

---

## 🔐 Authentication

**Session-based authentication required for all endpoints.**

### Login
```http
POST /login
Content-Type: application/x-www-form-urlencoded

username=john_doe
```

**Response:** `302 Redirect` to `/` with session cookie

### Logout
```http
GET /logout
```

**Response:** `302 Redirect` to `/login` (session cleared)

---

## 🔍 Search APIs

### 1. HTML Search Page
```http
GET /search?q=Python&type=auto&prefecture=tokyo&limit=20
```

**Parameters:**
- `q` - Search query (required)
- `type` - `auto` (default) or `title` 
- `prefecture` - Filter: `tokyo`, `osaka`, `kyoto`, etc.
- `limit` - Results per page: `10`, `20`, `50`

**Response:** HTML page with company-grouped search results

**Template Data Structure:**
```javascript
{
  query: "Python",
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
          content: "東京を拠点とするIT企業です...",
          matched_terms: ["python"],
          score: 1.95,
          id: "url_001"
        }
      ]
    }
  ],
  total_found: 15,
  total_companies: 8,
  search_time: 0.156
}
```

### 2. JSON Search API
```http
GET /api/search?q=Python&limit=10
```

**Parameters:**
- `q` - Search query (required)
- `limit` - Max results (default: 10)

**Response:**
```json
{
  "results": [
    {
      "id": "url_001",
      "title": "株式会社東京テクノロジー - メインサイト", 
      "content": "東京を拠点とするIT企業です...",
      "url": "https://tokyo-tech.co.jp",
      "score": 1.95,
      "matched_terms": ["python"]
    }
  ],
  "total_found": 15,
  "query": "Python",
  "search_time": 0.156
}
```

---

## 📥 CSV Export API

```http
GET /api/download-csv?q=Python&prefecture=tokyo
```

**Authentication:** Required (session-based)

**Parameters:**
- `q` - Search query (required)
- `type` - `auto` (default) or `title`
- `prefecture` - Optional filter

**Response:** CSV file download (UTF-8 BOM)

**CSV Columns:**
```
Company_Number,Company_Name,Company_Tel,Company_Industry,Prefecture,URL_Name,URL,Content,Matched_Terms,ID
```

**Features:**
- File-based caching for performance
- Company information repeated per URL
- Sorted by company_number
- Matched terms separated by `|`

---

## 📊 Statistics API

```http
GET /api/stats
```

**Response:**
```json
{
  "total_documents": 150,
  "engine_type": "Whoosh",
  "cache_hits": 45,
  "cache_misses": 12,
  "cache_size": 32,
  "cache_max_size": 128
}
```

---

## 📚 Search History

```http
GET /history?show_all=true
```

**Parameters:**
- `show_all` - `false` (8 entries) or `true` (up to 100)

**Response:** HTML page with search history table

**Template Data:**
```javascript
{
  searches: [
    {
      timestamp: "2024-03-15T14:30:22.123456",
      query: "python",
      search_type: "auto",
      results_count: 12,
      search_time: 0.156,
      prefecture: "tokyo"
    }
  ],
  total_searches: 45,
  show_all: false
}
```

---

## 🏆 Rankings Page

```http
GET /rankings
```

**Response:** HTML page with popular keyword rankings

**Template Data:**
```javascript
{
  queries: [
    {
      query: "python",
      count: 23,
      percentage: 15.3
    },
    {
      query: "ai",
      count: 18, 
      percentage: 12.0
    }
  ],
  stats: {
    total_queries: 150,
    unique_queries: 45,
    top_query: "python"
  }
}
```

---

## 📝 Data Management APIs

### Add Single Record
```http
POST /api/add_document
Content-Type: application/json

{
  "id": "url_001",
  "title": "株式会社東京テクノロジー - メインサイト",
  "content": "東京を拠点とするIT企業です...",
  "company_name": "株式会社東京テクノロジー",
  "company_number": "1010001000001",
  "company_tel": "03-1234-5678", 
  "company_industry": "情報通信業",
  "prefecture": "tokyo",
  "url_name": "メインサイト",
  "url": "https://tokyo-tech.co.jp"
}
```

**Response:**
```json
{"success": true, "message": "Document added successfully"}
```

### Add Multiple Records
```http
POST /api/add_documents
Content-Type: application/json

{
  "documents": [
    {
      "id": "url_001",
      "title": "Company A",
      "content": "Content here..."
      // ... other fields
    },
    {
      "id": "url_002", 
      "title": "Company B",
      "content": "More content..."
      // ... other fields
    }
  ]
}
```

**Response:**
```json
{"success": true, "message": "2 documents added successfully"}
```

### Clear Index
```http
POST /api/clear_index
```

**Response:**
```json
{"success": true, "message": "Index cleared successfully"}
```

### Optimize Index  
```http
POST /api/optimize_index
```

**Response:**
```json
{"success": true, "message": "Index optimized successfully"}
```

---

## ⚠️ Error Responses

All APIs return consistent error format:

```json
{"error": "Error message description"}
```

**Common HTTP Status Codes:**
- `400` - Bad Request (missing parameters)
- `401` - Unauthorized (login required)  
- `500` - Internal Server Error

---

## 💡 Usage Examples

### AJAX Search
```javascript
fetch('/api/search?q=Python&limit=5')
  .then(response => response.json())
  .then(data => {
    console.log(`Found ${data.total_found} results`);
    data.results.forEach(result => {
      console.log(result.title);
    });
  });
```

### CSV Download Trigger
```javascript
// Trigger download
const params = new URLSearchParams({
  q: 'Python',
  prefecture: 'tokyo'
});
window.location = `/api/download-csv?${params}`;
```

### Add Company Record
```javascript
fetch('/api/add_document', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    id: 'url_001',
    title: 'New Company',
    content: 'Company description...',
    company_name: '株式会社新会社',
    company_number: '1010001000999',
    prefecture: 'tokyo'
  })
})
.then(response => response.json())
.then(data => console.log(data.message));
```

---

## 🎯 Frontend Integration Tips

1. **Session Management** - Handle 401 redirects to login
2. **Japanese Text** - Queries normalized automatically
3. **Company Grouping** - Use HTML endpoints for grouped results
4. **CSV Downloads** - Check authentication before triggering
5. **Error Handling** - Parse JSON error responses
6. **Caching** - CSV/search results cached server-side

**That's it!** Clean, structured API reference for easy frontend integration.