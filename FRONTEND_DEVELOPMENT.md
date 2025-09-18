# Frontend Development Guide
**EOS - Japanese Enterprise Search Engine**

Complete setup and development guide for frontend developers working on the EOS platform.

---

## 📋 Table of Contents

### **Getting Started**
- [🪟 Windows uv Installation](#-windows-uv-installation) - Install the Python package manager
- [🚀 Running the Application](#-running-the-application) - Start the development server

### **Understanding the Project**
- [📁 Project Folder Structure](#-project-folder-structure) - Navigate the codebase
- [🎨 Frontend-Specific Folders](#-frontend-specific-folders) - Where to make UI/UX changes

### **Development Resources**
- [🔗 Development URLs](#useful-development-urls) - Test pages and APIs
- [🔧 Jinja2 Templates Explained](#understanding-jinja2-syntax-for-frontend-developers) - Server-side templating for React/Vue developers
- [⚡ JavaScript/AJAX Integration](#javascript-ajax-integration) - How to call APIs from frontend
- [📚 API Documentation](#api-documentation) - Complete integration guide

---

## 🪟 Windows uv Installation

EOS uses `uv` as the Python package manager for fast dependency management. Here's how to install it on Windows:

### **Method 1: PowerShell (Recommended)**
Open PowerShell as Administrator and run:

```powershell
# Install uv using the official installer
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

### **Method 2: Using pip**
If you already have Python installed:

```powershell
pip install uv
```

### **Method 3: Using Scoop**
If you have Scoop package manager:

```powershell
scoop install uv
```

### **Verify Installation**
Check if uv is installed correctly:

```powershell
uv --version
# Should output something like: uv 0.1.x
```

---

## 🚀 Running the Application

### **Development Workflow**

1. **Clone the repository:**
   ```bash
   git clone https://github.com/lorentzbao/eos-V2.git
   cd eos-V2
   ```

2. **Switch to frontend development branch:**
   ```bash
   git checkout frontend-dev
   ```

3. **Sync with main branch (before starting work):**
   ```bash
   git pull origin main
   git push origin frontend-dev
   ```

4. **Install dependencies:**
   ```bash
   uv sync
   ```

5. **Start the server:**
   ```bash
   uv run python run.py
   ```

6. **Open browser:** Navigate to http://127.0.0.1:5000

7. **Login:** Use any username (e.g., "frontend_dev")

8. **Make changes:** Edit templates, CSS, or JavaScript files

9. **Refresh browser:** Changes are automatically reloaded in debug mode

10. **Commit your changes:**
    ```bash
    git add .
    git commit -m "Describe your changes"
    git push origin frontend-dev
    ```

### **Stopping the Server**
- Press `Ctrl + C` in the terminal
- Or close the PowerShell/Command Prompt window

---

## 📁 Project Folder Structure

Understanding the project structure helps you locate files for frontend development:

```
eos/
├── 📁 app/                          # Main application code
│   ├── 📄 API_REFERENCE.md          # Complete API documentation
│   ├── 📁 routes/                   # URL routing and view logic
│   │   ├── 📄 main.py               # Main pages (/, /search, /login)
│   │   └── 📄 api.py                # JSON API endpoints
│   ├── 📁 services/                 # Backend business logic
│   └── 📄 __init__.py               # Flask app initialization
│
├── 📁 templates/                    # 🎨 HTML Templates (FRONTEND)
│   ├── 📄 index.html                # Main search page
│   ├── 📄 search.html               # Search results page
│   ├── 📄 login.html                # Login form
│   ├── 📄 rankings.html             # Popular rankings page
│   └── 📄 history.html              # Search history page
│
├── 📁 static/                       # 🎨 Static Assets (FRONTEND)
│   ├── 📁 css/
│   │   └── 📄 style.css             # Main stylesheet
│   ├── 📁 js/                       # JavaScript files
│   └── 📁 images/                   # Images and icons
│
├── 📁 conf/                         # Configuration files
│   ├── 📄 config.yaml               # Main app configuration
│   └── 📄 *.yaml                    # Data processing configs
│
├── 📁 data/                         # Data and search indexes
│   ├── 📁 raw/                      # Raw company data
│   ├── 📁 tokenized/                # Processed data
│   └── 📁 indexes/                  # Search indexes
│
├── 📁 scripts/                      # Data processing scripts
└── 📄 run.py                        # Application entry point
```

## 🎨 Frontend-Specific Folders

### **`templates/` Directory - HTML Templates**
This is where you'll spend most of your time for UI changes:

```
templates/
├── 📄 index.html                    # 🏠 Main search interface
│   ├── Search form with auto-suggestions
│   ├── Prefecture and status filters
│   └── Popular queries display
│
├── 📄 search.html                   # 🔍 Search results page
│   ├── Company-grouped results display
│   ├── Pagination controls
│   ├── CSV download button
│   └── Search refinement options
│
├── 📄 login.html                    # 🔐 User authentication
│   └── Simple username form
│
├── 📄 rankings.html                 # 📊 Analytics dashboard
│   ├── Popular search queries
│   ├── Top keywords
│   └── Search statistics
│
└── 📄 history.html                  # 📚 User search history
    ├── Recent searches display
    └── Search history pagination
```

**Template Technology:** Jinja2 templating engine (Flask's template system)

### **`static/` Directory - Frontend Assets**

```
static/
├── 📁 css/
│   └── 📄 style.css                 # 🎨 Main stylesheet
│       ├── Bootstrap 5 customizations
│       ├── Search interface styling
│       ├── Results display formatting
│       └── Responsive design rules
│
├── 📁 js/                           # 📝 JavaScript functionality
│   ├── Search auto-suggestions
│   ├── Form validation
│   ├── AJAX API calls
│   └── UI interactions
│
└── 📁 images/                       # 🖼️ Static images
    ├── Logo and icons
    └── UI graphics
```

### **Key Frontend Files to Modify**

| File | Purpose | When to Edit |
|------|---------|-------------|
| `templates/index.html` | Main search page | Change search interface, add filters |
| `templates/search.html` | Results display | Modify result layout, add features |
| `static/css/style.css` | Styling | Change colors, layout, responsive design |
| `static/js/*.js` | Interactivity | Add AJAX calls, form validation |
| `app/routes/main.py` | Page logic | Modify data passed to templates |
| `app/routes/api.py` | API endpoints | Add new JSON endpoints |

### **UI/UX Framework**
- **CSS Framework:** Bootstrap 5
- **Icons:** Bootstrap Icons
- **JavaScript:** Vanilla JS (no jQuery dependency)
- **Responsive:** Mobile-first design
- **Japanese Support:** UTF-8 encoding, proper font handling

### **Development Tips**

1. **Template Changes:** Automatically reloaded in debug mode
2. **CSS Changes:** Refresh browser to see updates
3. **JavaScript Changes:** Hard refresh (Ctrl+F5) may be needed
4. **Configuration Changes:** Restart server required

This structure separation makes it easy to focus on frontend development while understanding how data flows from the backend through templates to the browser.

---

## 🔗 Development Resources

### **Useful Development URLs**

#### **HTML Pages (Browser Navigation)**
| URL | Purpose | Priority |
|-----|---------|----------|
| `http://127.0.0.1:5000/` | Main search interface | **High** |
| `http://127.0.0.1:5000/login` | Login page | **High** |
| `http://127.0.0.1:5000/search?q=Python` | Search results page | **High** |
| `http://127.0.0.1:5000/rankings` | Popular rankings | Medium |
| `http://127.0.0.1:5000/history` | Search history | Medium |

#### **JSON APIs (JavaScript/AJAX)**
| URL | Purpose | Priority |
|-----|---------|----------|
| `http://127.0.0.1:5000/api/search?q=test` | JSON search API | **High** |
| `http://127.0.0.1:5000/api/prefectures` | Prefecture selector data | **High** |
| `http://127.0.0.1:5000/api/download-csv?q=test` | CSV download | Medium |
| `http://127.0.0.1:5000/api/stats` | Engine statistics | Medium |

---

## 🔧 Understanding Jinja2 Syntax for Frontend Developers

If you're coming from React/Vue/Angular, Jinja2 might look unfamiliar. Here's what you need to know:

**🔗 URL Generation:**
```html
<!-- Jinja2 (Flask) -->
<form action="{{ url_for('main.search') }}" method="GET">
<!-- Becomes: <form action="/search" method="GET"> -->

<a href="{{ url_for('main.rankings') }}">Rankings</a>
<!-- Becomes: <a href="/rankings">Rankings</a> -->

<script src="{{ url_for('static', filename='js/app.js') }}">
<!-- Becomes: <script src="/static/js/app.js"> -->
```

**📊 Data Display:**
```html
<!-- Variables -->
<h1>{{ company.company_name }}</h1>
<!-- Outputs: <h1>株式会社東京AIソリューションズ</h1> -->

<p>Found {{ total_results }} companies</p>
<!-- Outputs: <p>Found 15 companies</p> -->
```

**🔄 Loops (like v-for or map):**
```html
<!-- Jinja2 -->
{% for company in grouped_results %}
  <div class="company">
    <h3>{{ company.company_name }}</h3>
    {% for url in company.urls %}
      <a href="{{ url.url }}">{{ url.url_name }}</a>
    {% endfor %}
  </div>
{% endfor %}
```

**❓ Conditionals (like v-if):**
```html
<!-- Jinja2 -->
{% if user_logged_in %}
  <button>Download CSV</button>
{% else %}
  <a href="{{ url_for('main.login') }}">Login</a>
{% endif %}

{% if results %}
  <p>Found {{ results|length }} results</p>
{% else %}
  <p>No results found</p>
{% endif %}
```

**🛠️ Common Jinja2 Patterns You'll See:**

| Jinja2 Syntax | Purpose | React/Vue Equivalent |
|---------------|---------|---------------------|
| `{{ variable }}` | Display data | `{variable}` or `{{variable}}` |
| `{% for item in list %}` | Loop through data | `.map()` or `v-for` |
| `{% if condition %}` | Conditional rendering | `{condition && <div>}` or `v-if` |
| `{{ url_for('route.name') }}` | Generate URLs | Router links |
| `{{ variable\|filter }}` | Apply filters | Computed properties/methods |

**📝 Editing Templates:**
1. **Find the template file** in `templates/` directory
2. **Locate the HTML section** you want to modify
3. **Keep Jinja2 syntax intact** - only modify HTML structure and CSS classes
4. **Add your HTML/CSS** around existing Jinja2 code
5. **Test changes** by refreshing the browser (auto-reload in debug mode)

---

## ⚡ JavaScript/AJAX Integration

Understanding how frontend JavaScript interacts with the backend APIs:

### **🔄 Two Types of Frontend Interactions:**

#### **1. HTML Pages (Server-Rendered)**
- **Forms submit to HTML endpoints** - Like `/search`, `/login`
- **Server renders complete pages** - Browser gets full HTML
- **Page refreshes** - Traditional form submission

```html
<!-- Form submits to HTML endpoint -->
<form action="{{ url_for('main.search') }}" method="GET">
  <input name="q" type="text" placeholder="Search...">
  <button type="submit">Search</button>
</form>
<!-- Submits to /search and gets back a complete HTML page -->
```

#### **2. JSON APIs (JavaScript-Driven)**
- **JavaScript calls `/api/xxx` endpoints** - Like `/api/search`, `/api/prefectures`
- **Server returns JSON data** - No HTML, just data
- **Dynamic updates** - No page refresh needed

```javascript
// JavaScript calls JSON API
async function searchCompanies(query) {
    const response = await fetch(`/api/search?q=${query}`);
    const data = await response.json();

    // Update page dynamically without refresh
    displayResults(data.grouped_results);
}
```

### **📱 Practical Examples:**

#### **Populate Dropdown from API**
```html
<!-- HTML: Empty dropdown in template -->
<select id="prefectureSelect">
  <option value="">All Prefectures</option>
  <!-- Options populated by JavaScript -->
</select>

<script>
// JavaScript: Calls API and populates dropdown
async function loadPrefectures() {
    const response = await fetch('/api/prefectures');
    const data = await response.json();

    const select = document.getElementById('prefectureSelect');
    data.prefectures.forEach(pref => {
        const option = document.createElement('option');
        option.value = pref.code;
        option.textContent = pref.name;
        select.appendChild(option);
    });
}

// Call when page loads
document.addEventListener('DOMContentLoaded', loadPrefectures);
</script>
```

#### **Dynamic Search without Page Reload**
```html
<!-- HTML: Search form and results container -->
<form id="searchForm">
  <input id="searchInput" type="text" placeholder="Search companies...">
  <button type="submit">Search</button>
</form>
<div id="searchResults"></div>

<script>
// JavaScript: Handles form submission with AJAX
document.getElementById('searchForm').addEventListener('submit', async (e) => {
    e.preventDefault(); // Prevent normal form submission

    const query = document.getElementById('searchInput').value;

    // Call JSON API instead of submitting form
    const response = await fetch(`/api/search?q=${query}`);
    const data = await response.json();

    // Update results without page refresh
    const resultsDiv = document.getElementById('searchResults');
    resultsDiv.innerHTML = `
        <h3>Found ${data.total_results} results</h3>
        ${data.grouped_results.map(company => `
            <div class="company">
                <h4>${company.company_name}</h4>
                <p>${company.company_address}</p>
            </div>
        `).join('')}
    `;
});
</script>
```

#### **Download CSV with JavaScript**
```javascript
// Trigger CSV download
function downloadSearchResults(query) {
    const params = new URLSearchParams({ q: query });

    // Create temporary download link
    const link = document.createElement('a');
    link.href = `/api/download-csv?${params}`;
    link.download = `search_results_${new Date().toISOString().slice(0,10)}.csv`;

    // Trigger download
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
}
```

### **🎯 When to Use Each Approach:**

| Use Case | Method | Why |
|----------|--------|-----|
| **Login/Logout** | HTML form submission | Simple redirect flow |
| **Main search** | HTML form submission | SEO-friendly, shareable URLs |
| **Filter dropdowns** | JavaScript + JSON API | Dynamic data loading |
| **Real-time search** | JavaScript + JSON API | No page refresh needed |
| **CSV download** | JavaScript + API | Better user experience |
| **Statistics display** | JavaScript + JSON API | Periodic updates |

### **🔧 Integration Pattern:**
1. **HTML template** provides the structure and initial data
2. **JavaScript** enhances with dynamic functionality
3. **JSON APIs** provide data for JavaScript to consume
4. **Forms** handle user input and navigation

This hybrid approach combines the best of server-side rendering (SEO, initial load) with client-side interactivity (dynamic updates, better UX).

---

### **API Documentation**
**👉 [Complete API Reference](./app/API_REFERENCE.md)** - Practical examples for every endpoint
- Authentication and session management
- Search APIs with filtering and pagination
- CSV export functionality
- Admin operations and statistics
- Complete JavaScript integration examples