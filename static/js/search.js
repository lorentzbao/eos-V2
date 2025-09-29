// Search functionality module
app.search = {
    // Search suggestions data
    suggestions: [],
    currentSuggestionIndex: -1,
    shouldShowDropdownOnFocus: true,

    // Initialize search suggestions for a specific input
    initSearchSuggestions(inputId) {
        const searchInput = document.getElementById(inputId);
        const suggestionsDropdown = document.getElementById('searchSuggestions');
        const suggestionsList = document.getElementById('suggestionsList');

        if (!searchInput || !suggestionsDropdown || !suggestionsList) {
            console.warn('Search suggestion elements not found');
            return;
        }

        // Use app's popular queries
        const popularQueries = app.state.popularQueries || [];

        // Initialize suggestions
        if (popularQueries.length > 0) {
            this.suggestions = popularQueries.map(item => ({
                text: item.query,
                count: item.count,
                type: 'ranking'
            }));
        }

        // Input event handler
        searchInput.addEventListener('input', () => {
            const query = searchInput.value.trim();
            this.getSuggestions(query, popularQueries, suggestionsList, suggestionsDropdown, searchInput);
        });

        // Focus event - do not show suggestions on focus
        searchInput.addEventListener('focus', () => {
            // Only handle focus styling, no dropdown
        });

        // Click event - show suggestions on click
        searchInput.addEventListener('click', () => {
            this.getSuggestions(searchInput.value.trim(), popularQueries, suggestionsList, suggestionsDropdown, searchInput);
            if (this.suggestions.length > 0) {
                suggestionsDropdown.style.display = 'block';
            }
        });

        // Keyboard navigation
        searchInput.addEventListener('keydown', (e) => {
            this.handleKeyNavigation(e, searchInput, suggestionsList, suggestionsDropdown);
        });

        // Pre-render suggestions but keep hidden
        if (popularQueries.length > 0) {
            this.renderSuggestions(suggestionsList, suggestionsDropdown, searchInput);
            suggestionsDropdown.style.display = 'none';
        }

        // Disable dropdown on search results page when page loads with query
        if (searchInput.value.trim() !== '' && window.location.pathname === '/search') {
            this.shouldShowDropdownOnFocus = false;
            suggestionsDropdown.style.display = 'none';
        }

        // Click outside to close
        document.addEventListener('click', (e) => {
            if (!searchInput.contains(e.target) && !suggestionsDropdown.contains(e.target)) {
                suggestionsDropdown.style.display = 'none';
                this.currentSuggestionIndex = -1;
            }
        });

        // Handle form submission
        const searchForm = searchInput.closest('form');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                if (!this.validateAndSubmit(searchInput)) {
                    e.preventDefault();
                }
            });
        }

        searchInput.focus();
    },

    // Get suggestions based on query
    getSuggestions(query, popularQueries, suggestionsList, suggestionsDropdown, searchInput) {
        const lowerQuery = query.toLowerCase();

        if (query.length === 0) {
            this.suggestions = popularQueries.map(item => ({
                text: item.query,
                count: item.count,
                type: 'ranking'
            }));
        } else {
            this.suggestions = popularQueries
                .filter(item => item.query.toLowerCase().includes(lowerQuery))
                .map(item => ({
                    text: item.query,
                    count: item.count,
                    type: 'ranking'
                }));
        }

        this.renderSuggestions(suggestionsList, suggestionsDropdown, searchInput);
    },

    // Render suggestions
    renderSuggestions(suggestionsList, suggestionsDropdown, searchInput) {
        suggestionsList.innerHTML = '';

        if (this.suggestions.length === 0) {
            suggestionsDropdown.style.display = 'none';
            return;
        }

        this.suggestions.forEach((suggestion, index) => {
            const item = document.createElement('div');
            item.className = 'suggestion-item';
            item.innerHTML = `
                <div class="suggestion-text">
                    <span class="suggestion-icon">🔍</span>
                    <span>${app.utils.escapeHtml(suggestion.text)}</span>
                </div>
                <span class="suggestion-count">${suggestion.count}</span>
            `;

            item.addEventListener('click', () => {
                this.selectSuggestion(suggestion.text, searchInput, suggestionsDropdown);
            });

            suggestionsList.appendChild(item);
        });

        // Show dropdown when we have suggestions (only when explicitly called from click)
        // suggestionsDropdown display is controlled by the calling function
        this.currentSuggestionIndex = -1;
    },

    // Select a suggestion
    selectSuggestion(text, searchInput, suggestionsDropdown) {
        searchInput.value = text;
        suggestionsDropdown.style.display = 'none';
        searchInput.focus();
    },

    // Update suggestion selection highlighting
    updateSuggestionSelection(suggestionsList) {
        const items = suggestionsList.querySelectorAll('.suggestion-item');
        items.forEach((item, index) => {
            if (index === this.currentSuggestionIndex) {
                item.classList.add('active');
            } else {
                item.classList.remove('active');
            }
        });
    },

    // Handle keyboard navigation
    handleKeyNavigation(e, searchInput, suggestionsList, suggestionsDropdown) {
        const items = suggestionsList.querySelectorAll('.suggestion-item');

        if (e.key === 'ArrowDown') {
            e.preventDefault();
            this.currentSuggestionIndex = Math.min(this.currentSuggestionIndex + 1, items.length - 1);
            this.updateSuggestionSelection(suggestionsList);
        } else if (e.key === 'ArrowUp') {
            e.preventDefault();
            this.currentSuggestionIndex = Math.max(this.currentSuggestionIndex - 1, -1);
            this.updateSuggestionSelection(suggestionsList);
        } else if (e.key === 'Enter') {
            e.preventDefault();
            if (this.currentSuggestionIndex >= 0 && items[this.currentSuggestionIndex]) {
                const suggestionText = this.suggestions[this.currentSuggestionIndex].text;
                this.selectSuggestion(suggestionText, searchInput, suggestionsDropdown);
                // Submit the form with the selected suggestion
                if (this.validateAndSubmit(searchInput)) {
                    const form = searchInput.closest('form');
                    if (form) {
                        form.dispatchEvent(new Event('submit'));
                    }
                }
            } else {
                // Normal form submission
                if (this.validateAndSubmit(searchInput)) {
                    const form = searchInput.closest('form');
                    if (form) {
                        form.dispatchEvent(new Event('submit'));
                    }
                }
            }
        } else if (e.key === 'Escape') {
            suggestionsDropdown.style.display = 'none';
            this.currentSuggestionIndex = -1;
        }
    },

    // Show dropdown if has data
    showDropdownIfHasData(popularQueries, suggestionsDropdown) {
        if (popularQueries.length > 0 && this.shouldShowDropdownOnFocus) {
            suggestionsDropdown.style.display = 'block';
        }
    },

    // Validate and submit form
    validateAndSubmit(searchInput) {
        const query = searchInput.value.trim();
        if (query === '') {
            // Visual feedback
            searchInput.classList.add('is-invalid');
            searchInput.focus();
            setTimeout(() => {
                searchInput.classList.remove('is-invalid');
            }, 1500);
            return false;
        }
        return true;
    },

    // Perform search
    async performSearch(params) {
        try {
            app.showLoading();

            const searchParams = new URLSearchParams(params);
            const response = await fetch(`/search?${searchParams.toString()}`);

            if (!response.ok) {
                throw new Error(`Search failed: ${response.status}`);
            }

            const data = await response.json();
            app.state.searchResults = data;

            return data;

        } catch (error) {
            console.error('Search error:', error);
            throw error;
        } finally {
            app.hideLoading();
        }
    }
};