# TODO - EOS Project Task Tracker

This document tracks ongoing development tasks, improvements, and technical debt for the EOS Japanese Enterprise Search Engine project.

## Current Tasks

### Frontend-dev Integration (In Progress)
- [x] Create integrate-frontend-dev branch
- [x] Merge frontend-dev into integration branch
- [x] Restore CLAUDE.md and TODO.md from master
- [x] Test basic application startup
- [~] Fix and enhance search functionality
  - [x] Implement dynamic city/district dropdown based on prefecture selection
  - [x] Add backend support for city filtering
  - [x] Implement CUST_STATUS2 filtering for target selection (白地・過去 with OR logic)
  - [x] Sync prefecture dropdown with actual indexes (tokyo, osaka, kochi)
  - [x] Implement real-time search suggestions update (incremental in-memory)
  - [ ] Implement regional_office, branch, solicitor filtering for 契約 target
- [x] Add missing API endpoints
  - [x] `/api/user-rankings` - User search count rankings
  - [x] `/api/prefectures` - Dynamic prefecture list from config (already existed)
  - [x] `/api/cities/<prefecture>` - Cities by prefecture
- [x] Fix rankings page functionality (user rankings now load from search logs)
- [ ] Fix history page functionality
- [ ] Update documentation for SPA architecture

### Documentation
- [x] Create comprehensive frontend development guide (FRONTEND_DEVELOPMENT.md)
- [x] Create complete API reference with examples (app/API_REFERENCE.md)
- [x] Restructure README.md with improved organization
- [x] Add CLAUDE.md for AI assistant guidance
- [x] Add INTEGRATION_PLAN.md for frontend-dev merge
- [ ] Create ADMIN_GUIDE.md for data processing and administration

### Features

#### High Priority
- [x] Implement dynamic city/district dropdown (completed - loads from prefecture_cities.json)
- [ ] Add pagination support for search results (currently limited by `limit` parameter)
- [ ] Implement search result sorting options (relevance, date, company name)
- [ ] Add search query validation and sanitization
- [ ] Create admin dashboard for index management

#### Medium Priority
- [ ] Add CSV export progress indicator for large result sets
- [ ] Implement search suggestions/autocomplete from index data
- [ ] Add search filters: date range, industry classification, employee count
- [ ] Create batch document upload interface (currently API-only)
- [ ] Add search result preview/snippet highlighting

#### Low Priority
- [ ] Add user preferences (default prefecture, results per page)
- [ ] Implement saved searches feature
- [ ] Add search result bookmarking
- [ ] Create search analytics dashboard

### Performance Optimization
- [ ] Add Redis caching layer for frequently accessed searches
- [ ] Implement CSV cache expiration/cleanup strategy
- [ ] Optimize grouped results aggregation for large result sets
- [ ] Add database for search history (currently file-based)
- [ ] Profile and optimize tokenization pipeline for very large datasets (>100K records)
- [ ] Optimize user rankings sorting (currently O(n log n) on every request)
  - Option 1: Cache sorted rankings, invalidate on update
  - Option 2: Use heapq.nlargest() for O(n + k log k) complexity
  - Only needed if user count exceeds ~1000 users

### Testing
- [ ] Add integration tests for multi-index search routing
- [ ] Create end-to-end tests for search workflow
- [ ] Add performance benchmarks for tokenization and search
- [ ] Implement automated testing for Japanese text processing edge cases
- [ ] Add CSV export format validation tests

### Infrastructure
- [ ] Set up CI/CD pipeline (GitHub Actions)
- [ ] Add Docker containerization
- [ ] Create production deployment guide with nginx/gunicorn
- [ ] Set up automated index backup strategy
- [ ] Add monitoring and alerting (search performance, error rates)

### Code Quality
- [ ] Add type hints to all service layer functions
- [ ] Improve error handling in API endpoints (return proper HTTP status codes)
- [ ] Refactor search service to separate concerns (search, filtering, grouping)
- [ ] Add logging configuration (currently minimal logging)
- [ ] Create coding standards document

### Security
- [ ] Implement proper authentication system (replace simple username-only session)
- [ ] Add CSRF protection for forms
- [ ] Implement rate limiting for API endpoints
- [ ] Add input validation for all user inputs
- [ ] Sanitize HTML content extraction to prevent XSS
- [ ] Add API key authentication for admin endpoints

## Technical Debt

### Code Refactoring
- [ ] Consolidate duplicate `get_search_service()` functions in main.py and api.py
- [ ] Extract CSV generation logic from api.py into separate service
- [ ] Refactor search result grouping logic for better maintainability
- [ ] Separate Hydra configuration logic from script business logic
- [ ] Create shared utilities module for common functions

### Data Management
- [ ] Implement automatic CSV cache cleanup (currently manual)
- [ ] Add index versioning for migrations
- [ ] Create data validation layer for incoming documents
- [ ] Implement incremental indexing (currently full rebuild only)
- [ ] Add data deduplication logic

### Frontend
- [ ] Remove any remaining jQuery dependencies (currently Bootstrap 5 + vanilla JS)
- [ ] Improve mobile responsiveness
- [ ] Add loading states for all AJAX operations
- [ ] Implement client-side form validation
- [ ] Add accessibility improvements (ARIA labels, keyboard navigation)

### Configuration
- [ ] Add environment-specific configuration files (dev, staging, production)
- [ ] Implement configuration validation on startup
- [ ] Document all configuration options with examples
- [ ] Add configuration migration guide for version upgrades

## Completed Tasks

### Phase 1: Data Architecture (Completed)
- [x] Reorganize data folder structure (raw/tokenized/indexes separation)
- [x] Update all scripts to use new data folder structure
- [x] Migrate existing data to new structure
- [x] Remove old data folder structure
- [x] Update configuration files for new paths

### Phase 2: Documentation (Completed)
- [x] Create FRONTEND_DEVELOPMENT.md with setup instructions
- [x] Add Windows uv installation guide
- [x] Document project folder structure
- [x] Add Jinja2 templating explanation with framework comparisons
- [x] Add JavaScript/AJAX integration guide
- [x] Create table of contents with section links
- [x] Completely refresh API_REFERENCE.md with practical examples
- [x] Add API Quick Reference table
- [x] Reorganize APIs by type (JSON vs HTML)
- [x] Add copy-paste ready code examples for all endpoints
- [x] Update README.md with documentation hierarchy
- [x] Create CLAUDE.md for AI assistant guidance

### Phase 3: Repository Cleanup (Completed)
- [x] Add outputs/ folder to .gitignore
- [x] Remove outputs/ from repository
- [x] Commit and push all documentation changes

## Ideas for Future Enhancement

### Search Features
- Multi-language support (English, Chinese)
- Fuzzy search for typos and variations
- Advanced query syntax (boolean operators, phrase search)
- Search within specific fields (company name only, content only)
- Related searches suggestions
- Search result export to Excel with formatting
- Custom result ranking algorithms

### Data Processing
- Support for PDF content extraction
- Image OCR for scanned documents
- Automatic data enrichment from external sources
- Real-time index updates (currently requires rebuild)
- Data quality scoring and validation

### Analytics
- Search performance analytics dashboard
- User behavior tracking
- Popular search trends over time
- Search success rate metrics
- A/B testing framework for search algorithms

### Integration
- REST API with OpenAPI/Swagger documentation
- Webhook support for index updates
- Integration with external CRM systems
- Export to various formats (JSON, XML, Parquet)
- GraphQL API option

### UI/UX
- Dark mode support
- Customizable search result layout
- Advanced filter builder with visual interface
- Search result comparison tool
- Collaborative search sessions
- Email alerts for saved searches

## Notes

### Priority Guidelines
- **High Priority**: Critical for core functionality or user experience
- **Medium Priority**: Improves functionality but not blocking
- **Low Priority**: Nice-to-have features

### Task Status
- `[ ]` - Not started
- `[x]` - Completed
- `[~]` - In progress
- `[!]` - Blocked/On hold

### Contributing
When working on tasks from this list:
1. Update the task status to `[~]` when starting
2. Create a feature branch: `git checkout -b feature/task-name`
3. Mark as `[x]` when completed
4. Move completed tasks to the "Completed Tasks" section with completion date

### Review Schedule
This TODO.md should be reviewed and updated:
- Weekly for active development
- Monthly for maintenance mode
- After each major release

---

**Last Updated**: 2025-10-06 (Updated after user rankings and search suggestions implementation)
**Next Review**: TBD
