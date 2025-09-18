# Frontend Development Guide
**EOS - Japanese Enterprise Search Engine**

Complete setup and development guide for frontend developers working on the EOS platform.

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

2. **Switch to development branch:**
   ```bash
   git checkout dev
   ```

3. **Install dependencies:**
   ```bash
   uv sync
   ```

4. **Start the server:**
   ```bash
   uv run python run.py
   ```

5. **Open browser:** Navigate to http://127.0.0.1:5000

6. **Login:** Use any username (e.g., "frontend_dev")

7. **Make changes:** Edit templates, CSS, or JavaScript files

8. **Refresh browser:** Changes are automatically reloaded in debug mode

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

**Template Technology:** Jinja2 templating engine
- Use `{{ variable }}` for data output
- Use `{% if condition %}` for logic
- Use `{% for item in list %}` for loops

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

### **API Documentation**
**👉 [Complete API Reference](./app/API_REFERENCE.md)** - Practical examples for every endpoint
- Authentication and session management
- Search APIs with filtering and pagination
- CSV export functionality
- Admin operations and statistics
- Complete JavaScript integration examples