# Frontend-dev Integration Plan

This document outlines the plan to integrate the `frontend-dev` branch into `master`.

## Overview

The `frontend-dev` branch introduces a complete frontend rewrite with SPA architecture. This is a **major breaking change** that requires careful integration.

## Integration Branch Strategy

```bash
# 1. Create integration branch
git checkout master
git pull origin master
git checkout -b integrate-frontend-dev

# 2. Merge frontend-dev
git merge frontend-dev

# 3. Resolve conflicts and issues (see below)

# 4. Test thoroughly

# 5. Create PR to master
gh pr create --title "Integrate SPA frontend from frontend-dev" --base master
```

## Critical Issues to Resolve

### 1. Restore Missing Documentation

**Files to restore from master:**
- `CLAUDE.md` - AI assistant guidance
- `TODO.md` - Task tracking

**Action:**
```bash
git checkout master -- CLAUDE.md TODO.md
git add CLAUDE.md TODO.md
```

**Rationale:** These files are essential for project continuity and were removed in frontend-dev.

### 2. Backend API Compatibility

**Problem:** Frontend-dev expects APIs that don't exist in master backend.

**Phase 1: Minimal Integration (Immediate)**

Create stub endpoints to prevent errors:

```python
# In app/routes/api.py

@api.route('/user-rankings')
def api_user_rankings():
    """Stub: User rankings - returns dummy data"""
    # TODO: Implement real user ranking logic
    return jsonify({
        'user_rankings': [
            {'username': 'デモユーザー', 'search_count': 100, 'rank': 1}
        ]
    })

@api.route('/create-list', methods=['POST'])
def api_create_list():
    """Stub: List creation - redirects to existing CSV download"""
    # TODO: Implement file generation and tracking
    data = request.get_json()
    # For now, return existing download endpoint
    return jsonify({
        'file_id': 'stub',
        'download_url': '/api/download-csv'
    })
```

**Phase 2: Full Implementation (Follow-up)**

Tasks to complete:
- [ ] Implement `/api/user-rankings` with real data from search_logs.json
- [ ] Add new search parameters (target, regional_office, branch, solicitor)
- [ ] Update search_logger to track new criteria
- [ ] Implement CSV file generation with tracking
- [ ] Add validation for conditional required fields

### 3. Route Behavior Change

**Problem:** `app/routes/main.py` completely different behavior:
- Master: Returns HTML templates
- Frontend-dev: Returns JSON

**Solution: Hybrid Approach (Recommended)**

Support both SPA and traditional modes:

```python
from flask import request, jsonify, render_template

@main.route('/search')
def search():
    """Search endpoint - supports both HTML and JSON"""

    # ... existing search logic ...

    # Check if client wants JSON (SPA mode)
    if request.headers.get('Accept') == 'application/json' or \
       request.args.get('format') == 'json':
        return jsonify({
            'query': query,
            'grouped_results': search_results.get('grouped_results', []),
            'total_found': search_results['total_found'],
            'total_companies': search_results.get('total_companies', 0),
            'search_time': search_results['search_time'],
            'processed_query': search_results['processed_query'],
            'prefecture': prefecture,
            'cust_status': cust_status,
            'limit': limit,
            'username': username,
            'stats': stats
        })

    # Traditional mode - check if templates exist
    try:
        return render_template('search.html', ...)
    except:
        # Fallback to app.html if search.html doesn't exist
        return render_template('app.html', ...)
```

**Alternative: Full SPA Commit**

If deciding to go full SPA:
1. Remove all old templates except `app.html`
2. All routes return JSON only
3. Update FRONTEND_DEVELOPMENT.md to reflect SPA architecture
4. Update API_REFERENCE.md with new response formats

### 4. CSS Organization

**Change:** Single `style.css` → 4 modular files

**Impact:** None (improvement)

**Action:** Keep frontend-dev version, delete old `style.css`

### 5. JavaScript Organization

**Change:** Single `search.js` → 7 modular files

**Impact:** Better maintainability

**Action:** Keep frontend-dev version

## Testing Strategy

### Unit Testing
```bash
# Test existing functionality still works
uv run pytest tests/test_search_engine.py
uv run pytest tests/test_api_routes.py
```

### Manual Testing Checklist

#### Critical Path
1. **Login Flow**
   - [ ] Login page loads
   - [ ] Can login with any username
   - [ ] Session persists
   - [ ] Redirects to home after login
   - [ ] Logout works

2. **Search Flow**
   - [ ] Search form renders
   - [ ] Can enter query
   - [ ] Search executes
   - [ ] Results display
   - [ ] Results grouped by company
   - [ ] CSV download works

3. **Navigation**
   - [ ] All sidebar links work
   - [ ] Page transitions smooth (no reload)
   - [ ] Browser back/forward work
   - [ ] Direct URL access works

4. **New Features**
   - [ ] Search suggestions on click
   - [ ] Rankings page shows 3 tables
   - [ ] History page shows search records
   - [ ] Brand colors display correctly

#### Edge Cases
- [ ] Empty search query handled
- [ ] Multi-index prefecture selection works
- [ ] Search with no results displays properly
- [ ] Long search queries don't break UI
- [ ] Japanese characters display correctly
- [ ] Mobile responsive (if applicable)

### Browser Testing
- [ ] Chrome
- [ ] Firefox
- [ ] Safari
- [ ] Edge

### Data Compatibility
- [ ] Existing indexes work
- [ ] Existing search_logs.json readable
- [ ] CSV cache files accessible
- [ ] No data corruption

## Documentation Updates Needed

### 1. Update FRONTEND_DEVELOPMENT.md

Add section on SPA architecture:

```markdown
## SPA Architecture

EOS uses a Single Page Application (SPA) architecture with client-side routing.

### Key Components
- **app.html** - Single HTML template
- **router.js** - Client-side navigation
- **pages.js** - Dynamic page rendering
- **app.js** - Application state management

### How It Works
1. Server sends `app.html` on initial load
2. JavaScript takes over routing
3. Pages render dynamically via AJAX
4. No page reloads during navigation
```

### 2. Update API_REFERENCE.md

Document new response formats:

```markdown
## API Response Format Changes

All HTML endpoints (`/search`, `/rankings`, `/history`) now support JSON responses:

### Request JSON Response
```javascript
fetch('/search?q=Python&prefecture=tokyo', {
    headers: { 'Accept': 'application/json' }
})
```

### Response
```json
{
    "query": "Python",
    "grouped_results": [...],
    "total_found": 42,
    ...
}
```
```

### 3. Update CLAUDE.md

Add SPA architecture section:

```markdown
## SPA Architecture (Frontend-dev Integration)

The application uses Single Page Application architecture:

- **Single Template:** `templates/app.html`
- **Client Routing:** `static/js/router.js`
- **Page Rendering:** `static/js/pages.js` (1087 lines)
- **State Management:** `window.app.state`

**Important:** Routes in `app/routes/main.py` now return JSON when `Accept: application/json` header is present, otherwise return HTML templates.

### Module Loading Order
1. app.js - Core state
2. auth.js - Authentication
3. router.js - Navigation
4. pages.js - Rendering
5. search.js - Search functionality
6. pagination.js - Pagination
7. csv-download.js - CSV exports
```

### 4. Update TODO.md

Add integration tasks:

```markdown
## Frontend-dev Integration Tasks

### Phase 1: Basic Integration (In Progress)
- [x] Create integrate-frontend-dev branch
- [x] Merge frontend-dev
- [x] Restore CLAUDE.md and TODO.md
- [ ] Add stub API endpoints
- [ ] Implement hybrid route responses
- [ ] Test basic functionality
- [ ] Update documentation

### Phase 2: Backend Implementation
- [ ] Implement /api/user-rankings
- [ ] Add new search parameters (target, regional_office, etc.)
- [ ] Update search_logger for new criteria
- [ ] Implement CSV file generation with tracking
- [ ] Add conditional validation

### Phase 3: Feature Completion
- [ ] Remove dummy data from pages.js
- [ ] Implement real user rankings
- [ ] Add CSV-per-history-item functionality
- [ ] Complete all WEBDESIGN.md requirements
```

## Rollback Plan

If integration fails, rollback strategy:

```bash
# Option 1: Reset integration branch
git checkout integrate-frontend-dev
git reset --hard master

# Option 2: Keep master untouched until verified
# (Recommended - don't merge to master until fully tested)

# Option 3: Create rollback tag before merging
git tag pre-frontend-integration master
git push origin pre-frontend-integration

# Then if needed:
git reset --hard pre-frontend-integration
```

## Deployment Considerations

### Development Environment
- Works with existing `uv run python run.py`
- No additional dependencies needed
- JavaScript modules load in correct order

### Production Environment
- Ensure all CSS/JS files are accessible
- Check static file serving configuration
- Verify CORS if API on different domain
- Test with production data volumes
- Monitor client-side JavaScript errors

### Performance
- SPA reduces server load (fewer full page renders)
- Initial page load includes all JS modules (~2-3KB total)
- Subsequent navigation faster (no reload)
- Monitor client-side memory usage

## Timeline

**Week 1: Basic Integration**
- Create branch and merge
- Resolve conflicts
- Add stub endpoints
- Basic testing

**Week 2: Testing & Documentation**
- Comprehensive testing
- Update all documentation
- Create PR for review

**Week 3: Backend Implementation**
- Implement missing APIs
- Remove dummy data
- Full feature testing

**Week 4: Review & Merge**
- Code review
- Final testing
- Merge to master
- Deploy to production

## Success Criteria

Integration is successful when:
- [ ] All existing functionality works
- [ ] No data loss or corruption
- [ ] SPA navigation smooth
- [ ] All tests pass
- [ ] Documentation updated
- [ ] No console errors
- [ ] Acceptable performance
- [ ] Team approval

## Questions to Resolve

1. **Template Strategy:** Keep hybrid (HTML + JSON) or full SPA?
2. **Dummy Data:** Leave in pages.js or remove immediately?
3. **API Versioning:** Create `/api/v2/` for new endpoints?
4. **Browser Support:** Which browsers must we support?
5. **Accessibility:** WCAG compliance requirements?

## Contacts

- **Frontend Developer:** [Name of developer who created frontend-dev]
- **Backend Lead:** [Your name]
- **Code Review:** [Team members]

---

**Created:** 2025-10-06
**Last Updated:** 2025-10-06
**Status:** Planning
