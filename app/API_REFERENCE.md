# API Reference
**EOS - Japanese Enterprise Search Engine**

Practical API usage guide for frontend developers. This documentation focuses on how to actually use each API endpoint with real examples.

---

## 📋 API Quick Reference

### **JSON APIs (`/api/xxx`) - For JavaScript/AJAX**
- [`GET /api/search`](#json-search-api) - Get search results as JSON data
- [`GET /api/prefectures`](#get-available-prefectures) - Get list of available prefecture indexes
- [`GET /api/cities/<prefecture>`](#get-cities-by-prefecture) - Get cities for a specific prefecture
- [`GET /api/popular-queries`](#get-popular-queries) - Get popular search terms and frequency
- [`GET /api/user-rankings`](#get-user-rankings) - Get user search count rankings
- [`GET /api/download-csv`](#download-search-results-as-csv) - Export search results to CSV file
- [`GET /api/stats`](#search-engine-statistics) - Get search engine statistics and performance metrics
- [`POST /api/add_document`](#add-single-document) - Add single document to search index
- [`POST /api/add_documents`](#batch-add-documents) - Add multiple documents at once
- [`POST /api/clear_index`](#clear-search-index) - Clear all documents from search index
- [`POST /api/optimize_index`](#optimize-search-index) - Optimize search index for better performance

### **HTML Pages - For Navigation/Forms**
- [`POST /login`](#login) - Authenticate user and start session
- [`GET /logout`](#logout) - End user session
- [`GET /search`](#main-search-html-page) - Get search results as HTML page
- [`GET /rankings`](#popular-rankings-html-page) - View popular search terms and statistics
- [`GET /history`](#search-history-html-page) - View user's search history

---

## 🚀 Getting Started

**Base URL:** `http://127.0.0.1:5000`

**Authentication:** Session-based (login required for all endpoints)

**Content-Type:** Most POST requests use `application/json`

---

## 🔐 Authentication APIs

### Login
**Purpose:** Authenticate user and start session

```http
POST /login
Content-Type: application/x-www-form-urlencoded

username=your_username
```

**How to use:**
```javascript
// Login with form data
async function login(username) {
    const formData = new FormData();
    formData.append('username', username);

    const response = await fetch('/login', {
        method: 'POST',
        body: formData
    });

    // Will redirect to main page on success
    if (response.ok && response.redirected) {
        window.location.href = '/';
    }
}

// Usage
login('frontend_developer');
```

### Logout
**Purpose:** End user session

```http
GET /logout
```

**How to use:**
```javascript
// Simple logout
function logout() {
    window.location.href = '/logout';
    // Will redirect to login page
}

// Or with fetch
async function logout() {
    await fetch('/logout');
    window.location.href = '/login';
}
```

---

## 🔍 Search APIs

### Main Search (HTML Page)
**Purpose:** Get search results as a rendered HTML page

```http
GET /search?q=Python&prefecture=tokyo&cust_status=白地&limit=20
```

**Parameters:**
- `q` (required) - Search query
- `prefecture` (optional) - `tokyo`, `osaka`, `kochi`
- `cust_status` (optional) - `白地` (prospects), `契約` (existing)
- `limit` (optional) - `10`, `20`, `50` (default: 10)

**How to use:**
```javascript
// Build search URL and navigate
function searchPage(query, options = {}) {
    const params = new URLSearchParams({ q: query });

    if (options.prefecture) params.append('prefecture', options.prefecture);
    if (options.custStatus) params.append('cust_status', options.custStatus);
    if (options.limit) params.append('limit', options.limit);

    window.location.href = `/search?${params}`;
}

// Usage examples
searchPage('Python 開発');
searchPage('AI', { prefecture: 'tokyo', custStatus: '白地', limit: 20 });
```

### JSON Search API
**Purpose:** Get search results as JSON data for AJAX calls

```http
GET /api/search?q=AI&prefecture=tokyo&city=渋谷区&limit=10
```

**Parameters:**
- `q` (required) - Search query
- `prefecture` (required) - `tokyo`, `osaka`, `kochi`
- `city` (optional) - City/district name (e.g., `渋谷区`, `新宿区`)
- `cust_status` (optional) - `白地|過去` (prospects OR past), `契約` (contract)
- `limit` (optional) - Results per page (default: 10)

**Response Format:**
```json
{
  "success": true,
  "query": "AI",
  "total_results": 8,
  "execution_time": 0.045,
  "grouped_results": [
    {
      "company_name": "株式会社東京AIソリューションズ",
      "jcn": "1270001234567",
      "company_address": "東京都新宿区西新宿2-8-1",
      "prefecture": "tokyo",
      "industry": "情報通信業",
      "urls": [
        {
          "id": "1270001234567_main",
          "url": "https://www.tokyo-ai.co.jp",
          "url_name": "メインサイト",
          "content": "人工知能で未来を創造...",
          "matched_terms": ["ai"],
          "score": 2.15
        }
      ]
    }
  ]
}
```

**How to use:**
```javascript
// Search function with error handling
async function searchAPI(query, options = {}) {
    const params = new URLSearchParams({ q: query });

    if (options.prefecture) params.append('prefecture', options.prefecture);
    if (options.city) params.append('city', options.city);
    if (options.custStatus) params.append('cust_status', options.custStatus);
    if (options.limit) params.append('limit', options.limit);

    try {
        const response = await fetch(`/api/search?${params}`);

        if (!response.ok) {
            throw new Error(`HTTP ${response.status}`);
        }

        const data = await response.json();

        if (!data.success) {
            throw new Error(data.error || 'Search failed');
        }

        return data;
    } catch (error) {
        console.error('Search error:', error);
        return { success: false, error: error.message };
    }
}

// Usage examples
const results = await searchAPI('Python');
if (results.success) {
    console.log(`Found ${results.total_results} companies`);
    displayResults(results.grouped_results);
}

// With filters including city
const filteredResults = await searchAPI('AI 機械学習', {
    prefecture: 'tokyo',
    city: '渋谷区',
    custStatus: '白地|過去',  // Use pipe | for OR logic
    limit: 20
});
```

**Practical Implementation:**
```javascript
// Complete search with loading state
async function performSearch() {
    const query = document.getElementById('searchInput').value;
    const prefecture = document.getElementById('prefectureSelect').value;
    const city = document.getElementById('citySelect').value;
    const custStatus = document.getElementById('custStatusSelect').value;

    // Show loading
    document.getElementById('searchResults').innerHTML = '<div class="spinner">Searching...</div>';

    const results = await searchAPI(query, { prefecture, city, custStatus, limit: 20 });

    if (results.success) {
        displaySearchResults(results);
    } else {
        showError(results.error);
    }
}

function displaySearchResults(data) {
    const container = document.getElementById('searchResults');

    if (data.grouped_results.length === 0) {
        container.innerHTML = '<p>No results found.</p>';
        return;
    }

    let html = `<h3>Found ${data.total_results} results (${data.execution_time}s)</h3>`;

    data.grouped_results.forEach(company => {
        html += `
            <div class="company-result">
                <h4>${company.company_name}</h4>
                <p class="company-info">${company.company_address} | ${company.industry}</p>
        `;

        company.urls.forEach(url => {
            html += `
                <div class="url-result">
                    <a href="${url.url}" target="_blank">${url.url_name}</a>
                    <span class="score">Score: ${url.score}</span>
                    <p>${url.content.substring(0, 200)}...</p>
                    <p class="matched-terms">Matched: ${url.matched_terms.join(', ')}</p>
                </div>
            `;
        });

        html += `</div>`;
    });

    container.innerHTML = html;
}
```

---

## 📊 Configuration APIs

### Get Available Prefectures
**Purpose:** Get list of available prefecture indexes for dropdown

```http
GET /api/prefectures
```

**Response:**
```json
{
  "prefectures": [
    {
      "code": "tokyo",
      "name": "Tokyo",
      "index_path": "data/indexes/tokyo"
    },
    {
      "code": "osaka",
      "name": "Osaka",
      "index_path": "data/indexes/osaka"
    },
    {
      "code": "kochi",
      "name": "Kochi",
      "index_path": "data/indexes/kochi"
    }
  ]
}
```

**How to use:**
```javascript
// Populate prefecture dropdown
async function loadPrefectures() {
    try {
        const response = await fetch('/api/prefectures');
        const data = await response.json();

        const select = document.getElementById('prefectureSelect');

        // Clear existing options
        select.innerHTML = '<option value="">All Prefectures</option>';

        // Add prefecture options
        data.prefectures.forEach(pref => {
            const option = document.createElement('option');
            option.value = pref.code;
            option.textContent = pref.name;
            select.appendChild(option);
        });

    } catch (error) {
        console.error('Failed to load prefectures:', error);
    }
}

// Call on page load
document.addEventListener('DOMContentLoaded', loadPrefectures);
```

### Get Cities by Prefecture
**Purpose:** Get list of cities/districts for a specific prefecture

```http
GET /api/cities/tokyo
```

**Response:**
```json
{
  "cities": [
    "千代田区",
    "中央区",
    "港区",
    "新宿区",
    "渋谷区",
    "豊島区"
  ]
}
```

**How to use:**
```javascript
// Load cities when prefecture changes
async function loadCities(prefecture) {
    if (!prefecture) {
        // Clear city dropdown if no prefecture selected
        document.getElementById('citySelect').innerHTML = '<option value="">All Cities</option>';
        return;
    }

    try {
        const response = await fetch(`/api/cities/${prefecture}`);
        const data = await response.json();

        const select = document.getElementById('citySelect');
        select.innerHTML = '<option value="">All Cities</option>';

        data.cities.forEach(city => {
            const option = document.createElement('option');
            option.value = city;
            option.textContent = city;
            select.appendChild(option);
        });

    } catch (error) {
        console.error('Failed to load cities:', error);
    }
}

// Attach to prefecture dropdown change event
document.getElementById('prefectureSelect').addEventListener('change', (e) => {
    loadCities(e.target.value);
});
```

### Get Popular Queries
**Purpose:** Get popular search terms with frequency counts

```http
GET /api/popular-queries
```

**Response:**
```json
[
  {
    "query": "Python 開発",
    "count": 45
  },
  {
    "query": "AI 機械学習",
    "count": 38
  },
  {
    "query": "クラウド",
    "count": 32
  }
]
```

**How to use:**
```javascript
// Display popular queries
async function loadPopularQueries() {
    try {
        const response = await fetch('/api/popular-queries');
        const queries = await response.json();

        const container = document.getElementById('popularQueries');
        container.innerHTML = '<h3>Popular Searches</h3>';

        const list = document.createElement('ul');
        queries.forEach(item => {
            const li = document.createElement('li');
            li.innerHTML = `
                <a href="#" onclick="searchWithQuery('${item.query}'); return false;">
                    ${item.query}
                </a>
                <span class="count">(${item.count} searches)</span>
            `;
            list.appendChild(li);
        });

        container.appendChild(list);
    } catch (error) {
        console.error('Failed to load popular queries:', error);
    }
}

function searchWithQuery(query) {
    document.getElementById('searchInput').value = query;
    performSearch();
}
```

### Get User Rankings
**Purpose:** Get user search count rankings

```http
GET /api/user-rankings?limit=10
```

**Parameters:**
- `limit` (optional) - Number of top users to return (default: 10)

**Response:**
```json
[
  {
    "username": "tanaka",
    "count": 156
  },
  {
    "username": "suzuki",
    "count": 142
  },
  {
    "username": "sato",
    "count": 128
  }
]
```

**How to use:**
```javascript
// Display user rankings leaderboard
async function loadUserRankings(limit = 10) {
    try {
        const response = await fetch(`/api/user-rankings?limit=${limit}`);
        const rankings = await response.json();

        const container = document.getElementById('userRankings');
        container.innerHTML = '<h3>Top Users</h3>';

        const table = document.createElement('table');
        table.className = 'rankings-table';
        table.innerHTML = `
            <thead>
                <tr>
                    <th>Rank</th>
                    <th>Username</th>
                    <th>Searches</th>
                </tr>
            </thead>
            <tbody>
            </tbody>
        `;

        const tbody = table.querySelector('tbody');
        rankings.forEach((user, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${index + 1}</td>
                <td>${user.username}</td>
                <td>${user.count}</td>
            `;
            tbody.appendChild(row);
        });

        container.appendChild(table);
    } catch (error) {
        console.error('Failed to load user rankings:', error);
    }
}

// Load rankings on page load
document.addEventListener('DOMContentLoaded', () => {
    loadUserRankings();
});
```

---

## 📥 Data Export API

### Download Search Results as CSV
**Purpose:** Export search results to CSV file

```http
GET /api/download-csv?q=Python&prefecture=tokyo&cust_status=白地
```

**Parameters:** Same as search API

**Response:** CSV file download with headers:
```csv
id,jcn,company_name_kj,company_address_all,prefecture,city,main_domain_url,CUST_STATUS2,LARGE_CLASS_NAME,MIDDLE_CLASS_NAME,CURR_SETLMNT_TAKING_AMT,EMPLOYEE_ALL_NUM,url,url_name,content_tokens,token_count,matched_terms,score
```

**How to use:**
```javascript
// Download CSV for current search
function downloadCSV(query, options = {}) {
    const params = new URLSearchParams({ q: query });

    if (options.prefecture) params.append('prefecture', options.prefecture);
    if (options.custStatus) params.append('cust_status', options.custStatus);

    // Create temporary download link
    const url = `/api/download-csv?${params}`;
    const link = document.createElement('a');
    link.href = url;
    link.download = `search_results_${new Date().toISOString().slice(0,10)}.csv`;

    // Trigger download
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}

// Add to download button
document.getElementById('downloadBtn').addEventListener('click', () => {
    const query = document.getElementById('searchInput').value;
    const prefecture = document.getElementById('prefectureSelect').value;
    const custStatus = document.getElementById('custStatusSelect').value;

    if (!query) {
        alert('Please enter a search query first');
        return;
    }

    downloadCSV(query, { prefecture, custStatus });
});

// Download with loading feedback
async function downloadWithFeedback(query, options = {}) {
    const btn = document.getElementById('downloadBtn');
    const originalText = btn.textContent;

    btn.textContent = 'Preparing Download...';
    btn.disabled = true;

    try {
        downloadCSV(query, options);

        // Show success message
        btn.textContent = 'Downloaded!';
        setTimeout(() => {
            btn.textContent = originalText;
            btn.disabled = false;
        }, 2000);

    } catch (error) {
        btn.textContent = 'Download Failed';
        setTimeout(() => {
            btn.textContent = originalText;
            btn.disabled = false;
        }, 2000);
    }
}
```

---

## 📈 Analytics APIs

### Popular Rankings (HTML Page)
**Purpose:** View popular search terms and statistics

```http
GET /rankings
```

**How to use:**
```javascript
// Navigate to rankings page
function showRankings() {
    window.location.href = '/rankings';
}

// Or load rankings data in a modal/section
async function loadRankingsData() {
    // Note: This loads the HTML page, you'd need a separate JSON endpoint for pure data
    const response = await fetch('/rankings');
    const html = await response.text();

    // Parse or display HTML
    document.getElementById('rankingsContainer').innerHTML = html;
}
```

### Search History (HTML Page)
**Purpose:** View user's search history

```http
GET /history?limit=8&show_all=false
```

**Parameters:**
- `limit` (optional) - Number of recent searches (default: 8)
- `show_all` (optional) - Show all history: `true`/`false` (default: false)

**How to use:**
```javascript
// Navigate to history page
function showHistory(showAll = false) {
    const url = showAll ? '/history?show_all=true' : '/history';
    window.location.href = url;
}

// Load recent searches only
function showRecentHistory() {
    window.location.href = '/history?limit=5';
}
```

---

## 🛠️ Admin APIs

### Add Single Document
**Purpose:** Add a single document to the search index

```http
POST /api/add_document
Content-Type: application/json

{
  "id": "company_001_main",
  "title": "株式会社サンプル",
  "content": "サンプル企業の説明文...",
  "url": "https://sample.co.jp",
  "prefecture": "tokyo"
}
```

**How to use:**
```javascript
async function addDocument(doc) {
    try {
        const response = await fetch('/api/add_document', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(doc)
        });

        const result = await response.json();

        if (result.success) {
            console.log(`Document added: ${result.document_id}`);
            return true;
        } else {
            console.error('Failed to add document:', result.error);
            return false;
        }
    } catch (error) {
        console.error('Error adding document:', error);
        return false;
    }
}

// Usage
const newDoc = {
    id: 'sample_company_main',
    title: '株式会社サンプル',
    content: 'AI、機械学習、Python開発を行う企業です。',
    url: 'https://sample.co.jp',
    prefecture: 'tokyo'
};

addDocument(newDoc);
```

### Batch Add Documents
**Purpose:** Add multiple documents at once

```http
POST /api/add_documents
Content-Type: application/json

{
  "documents": [
    {
      "id": "doc1",
      "title": "Company A",
      "content": "Description A..."
    },
    {
      "id": "doc2",
      "title": "Company B",
      "content": "Description B..."
    }
  ]
}
```

**How to use:**
```javascript
async function addMultipleDocuments(documents) {
    try {
        const response = await fetch('/api/add_documents', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ documents })
        });

        const result = await response.json();

        if (result.success) {
            console.log(`Added ${result.added_count} documents, ${result.failed_count} failed`);
            return result;
        } else {
            console.error('Batch add failed:', result.error);
            return null;
        }
    } catch (error) {
        console.error('Error in batch add:', error);
        return null;
    }
}

// Usage with progress tracking
async function importDocuments(docList) {
    const batchSize = 10;
    const total = docList.length;

    for (let i = 0; i < total; i += batchSize) {
        const batch = docList.slice(i, i + batchSize);

        console.log(`Processing batch ${Math.floor(i/batchSize) + 1}/${Math.ceil(total/batchSize)}`);

        const result = await addMultipleDocuments(batch);

        if (!result) {
            console.error(`Batch ${i/batchSize + 1} failed`);
            break;
        }

        // Update progress UI
        updateProgress((i + batch.length) / total * 100);
    }
}
```

### Search Engine Statistics
**Purpose:** Get search engine statistics and performance metrics

```http
GET /api/stats
```

**Response:**
```json
{
  "index_stats": {
    "total_documents": 1250,
    "index_size_mb": 45.6,
    "last_updated": "2025-01-15T10:30:00Z"
  },
  "search_stats": {
    "total_searches": 2340,
    "unique_queries": 890,
    "average_results_per_query": 12.5
  },
  "performance": {
    "average_search_time_ms": 45,
    "cache_hit_rate": 0.78
  }
}
```

**How to use:**
```javascript
async function getStats() {
    try {
        const response = await fetch('/api/stats');
        const stats = await response.json();

        // Display stats in UI
        document.getElementById('totalDocs').textContent = stats.index_stats.total_documents;
        document.getElementById('indexSize').textContent = `${stats.index_stats.index_size_mb} MB`;
        document.getElementById('totalSearches').textContent = stats.search_stats.total_searches;
        document.getElementById('avgSearchTime').textContent = `${stats.performance.average_search_time_ms}ms`;

        return stats;
    } catch (error) {
        console.error('Failed to fetch stats:', error);
        return null;
    }
}

// Update stats dashboard every 30 seconds
setInterval(getStats, 30000);
```

### Clear Search Index
**Purpose:** Clear all documents from search index

```http
POST /api/clear_index
```

**How to use:**
```javascript
async function clearIndex() {
    const confirmed = confirm('Are you sure you want to clear the entire search index? This cannot be undone.');

    if (!confirmed) return;

    try {
        const response = await fetch('/api/clear_index', {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            alert(`Index cleared successfully. ${result.documents_removed} documents removed.`);
            // Refresh stats or redirect
            window.location.reload();
        } else {
            alert('Failed to clear index: ' + result.error);
        }
    } catch (error) {
        console.error('Error clearing index:', error);
        alert('Error clearing index');
    }
}

// Add to clear button with double confirmation
document.getElementById('clearIndexBtn').addEventListener('click', () => {
    const confirmation = prompt('Type "CLEAR" to confirm index deletion:');
    if (confirmation === 'CLEAR') {
        clearIndex();
    }
});
```

### Optimize Search Index
**Purpose:** Optimize search index for better performance

```http
POST /api/optimize_index
```

**How to use:**
```javascript
async function optimizeIndex() {
    const btn = document.getElementById('optimizeBtn');
    const originalText = btn.textContent;

    btn.textContent = 'Optimizing...';
    btn.disabled = true;

    try {
        const response = await fetch('/api/optimize_index', {
            method: 'POST'
        });

        const result = await response.json();

        if (result.success) {
            btn.textContent = 'Optimized!';
            console.log(`Optimization completed in ${result.optimization_time_ms}ms`);
            console.log(`Size reduced by ${result.size_reduction_mb}MB`);

            // Show success message
            showNotification(`Index optimized! Saved ${result.size_reduction_mb}MB in ${result.optimization_time_ms}ms`);
        } else {
            btn.textContent = 'Optimization Failed';
            console.error('Optimization failed:', result.error);
        }
    } catch (error) {
        btn.textContent = 'Error';
        console.error('Error optimizing index:', error);
    } finally {
        setTimeout(() => {
            btn.textContent = originalText;
            btn.disabled = false;
        }, 3000);
    }
}
```

---

## 🎯 Complete Integration Examples

### Search Interface with All Features
```javascript
class SearchInterface {
    constructor() {
        this.initializeElements();
        this.loadPrefectures();
        this.setupEventListeners();
    }

    initializeElements() {
        this.searchForm = document.getElementById('searchForm');
        this.searchInput = document.getElementById('searchInput');
        this.prefectureSelect = document.getElementById('prefectureSelect');
        this.citySelect = document.getElementById('citySelect');
        this.custStatusSelect = document.getElementById('custStatusSelect');
        this.resultsContainer = document.getElementById('searchResults');
        this.downloadBtn = document.getElementById('downloadBtn');
    }

    async loadPrefectures() {
        try {
            const response = await fetch('/api/prefectures');
            const data = await response.json();

            this.prefectureSelect.innerHTML = '<option value="">All Prefectures</option>';

            data.prefectures.forEach(pref => {
                const option = document.createElement('option');
                option.value = pref.code;
                option.textContent = pref.name;
                this.prefectureSelect.appendChild(option);
            });
        } catch (error) {
            console.error('Failed to load prefectures:', error);
        }
    }

    async loadCities(prefecture) {
        if (!prefecture) {
            this.citySelect.innerHTML = '<option value="">All Cities</option>';
            return;
        }

        try {
            const response = await fetch(`/api/cities/${prefecture}`);
            const data = await response.json();

            this.citySelect.innerHTML = '<option value="">All Cities</option>';

            data.cities.forEach(city => {
                const option = document.createElement('option');
                option.value = city;
                option.textContent = city;
                this.citySelect.appendChild(option);
            });
        } catch (error) {
            console.error('Failed to load cities:', error);
        }
    }

    setupEventListeners() {
        this.searchForm.addEventListener('submit', (e) => {
            e.preventDefault();
            this.performSearch();
        });

        this.downloadBtn.addEventListener('click', () => {
            this.downloadResults();
        });

        // Load cities when prefecture changes
        this.prefectureSelect.addEventListener('change', (e) => {
            this.loadCities(e.target.value);
        });

        // Auto-search on input (debounced)
        let timeout;
        this.searchInput.addEventListener('input', (e) => {
            clearTimeout(timeout);
            timeout = setTimeout(() => {
                if (e.target.value.length >= 2) {
                    this.performSearch();
                }
            }, 500);
        });
    }

    async performSearch() {
        const query = this.searchInput.value.trim();
        if (!query) return;

        const options = {
            prefecture: this.prefectureSelect.value,
            city: this.citySelect.value,
            custStatus: this.custStatusSelect.value,
            limit: 20
        };

        this.showLoading();

        const results = await searchAPI(query, options);

        if (results.success) {
            this.displayResults(results);
            this.downloadBtn.style.display = 'block';
        } else {
            this.showError(results.error);
        }
    }

    displayResults(data) {
        if (data.grouped_results.length === 0) {
            this.resultsContainer.innerHTML = '<div class="no-results">No results found.</div>';
            return;
        }

        let html = `
            <div class="results-header">
                <h3>Found ${data.total_results} results in ${data.execution_time}s</h3>
            </div>
        `;

        data.grouped_results.forEach(company => {
            html += `
                <div class="company-card">
                    <div class="company-header">
                        <h4>${company.company_name}</h4>
                        <span class="company-meta">${company.company_address} | ${company.industry}</span>
                    </div>
                    <div class="url-list">
            `;

            company.urls.forEach(url => {
                html += `
                    <div class="url-item">
                        <div class="url-header">
                            <a href="${url.url}" target="_blank" class="url-link">${url.url_name}</a>
                            <span class="score-badge">Score: ${url.score}</span>
                        </div>
                        <p class="url-content">${url.content.substring(0, 200)}...</p>
                        <div class="matched-terms">
                            Matched terms: ${url.matched_terms.map(term => `<span class="term">${term}</span>`).join(', ')}
                        </div>
                    </div>
                `;
            });

            html += `
                    </div>
                </div>
            `;
        });

        this.resultsContainer.innerHTML = html;
    }

    showLoading() {
        this.resultsContainer.innerHTML = `
            <div class="loading">
                <div class="spinner"></div>
                <p>Searching...</p>
            </div>
        `;
    }

    showError(error) {
        this.resultsContainer.innerHTML = `
            <div class="error">
                <p>Search failed: ${error}</p>
                <button onclick="location.reload()">Try Again</button>
            </div>
        `;
    }

    downloadResults() {
        const query = this.searchInput.value.trim();
        if (!query) {
            alert('Please enter a search query first');
            return;
        }

        downloadCSV(query, {
            prefecture: this.prefectureSelect.value,
            city: this.citySelect.value,
            custStatus: this.custStatusSelect.value
        });
    }
}

// Initialize search interface when page loads
document.addEventListener('DOMContentLoaded', () => {
    new SearchInterface();
});
```

This API reference provides practical, copy-paste examples for every endpoint. Each section shows not just what the API does, but exactly how to use it in real frontend code with proper error handling and user feedback.