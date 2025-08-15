document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('input[name="q"]');
    const suggestionsDropdown = document.getElementById('searchSuggestions');
    const suggestionsList = document.getElementById('suggestionsList');
    let currentSuggestionIndex = -1;
    let suggestions = [];
    let popularQueries = window.popularQueries || [];
    let shouldShowDropdownOnFocus = true;
    
    if (searchInput && suggestionsDropdown && suggestionsList) {
        // Search suggestions functionality using cached data
        function getSuggestions(query) {
            const lowerQuery = query.toLowerCase();
            
            if (query.length === 0) {
                // Show all popular queries when no input
                suggestions = popularQueries.map(item => ({
                    text: item.query,
                    count: item.count,
                    type: 'ranking'
                }));
            } else {
                // Filter suggestions that match the query
                suggestions = popularQueries
                    .filter(item => item.query.toLowerCase().includes(lowerQuery))
                    .map(item => ({
                        text: item.query,
                        count: item.count,
                        type: 'ranking'
                    }));
            }
            
            renderSuggestions();
        }
        
        function renderSuggestions() {
            suggestionsList.innerHTML = '';
            
            if (suggestions.length === 0) {
                suggestionsDropdown.style.display = 'none';
                return;
            }
            
            suggestions.forEach((suggestion, index) => {
                const item = document.createElement('div');
                item.className = 'suggestion-item';
                item.innerHTML = `
                    <div class="suggestion-text">
                        <span class="suggestion-icon">🔍</span>
                        <span>${suggestion.text}</span>
                    </div>
                    <span class="suggestion-count">${suggestion.count}</span>
                `;
                
                item.addEventListener('click', function() {
                    selectSuggestion(suggestion.text);
                });
                
                suggestionsList.appendChild(item);
            });
            
            // Always show dropdown when we have suggestions and input is focused
            if (document.activeElement === searchInput) {
                suggestionsDropdown.style.display = 'block';
            }
            currentSuggestionIndex = -1;
        }
        
        function selectSuggestion(text) {
            searchInput.value = text;
            suggestionsDropdown.style.display = 'none';
            searchInput.focus();
        }
        
        function updateSuggestionSelection() {
            const items = suggestionsList.querySelectorAll('.suggestion-item');
            items.forEach((item, index) => {
                if (index === currentSuggestionIndex) {
                    item.classList.add('active');
                } else {
                    item.classList.remove('active');
                }
            });
        }
        
        // Input event handler - instant suggestions
        searchInput.addEventListener('input', function() {
            const query = this.value.trim();
            getSuggestions(query); // Instant, no delay needed
        });
        
        // Focus event - show popular searches instantly
        searchInput.addEventListener('focus', function() {
            if (shouldShowDropdownOnFocus) {
                showDropdownIfHasData();
                getSuggestions(this.value.trim());
            } else {
                // Reset flag after first focus on search results page
                shouldShowDropdownOnFocus = true;
            }
        });
        
        // Click event - ensure dropdown shows even on repeated clicks
        searchInput.addEventListener('click', function() {
            showDropdownIfHasData();
            getSuggestions(this.value.trim());
        });
        
        // Helper function to show dropdown reliably
        function showDropdownIfHasData() {
            if (popularQueries.length > 0 && shouldShowDropdownOnFocus) {
                suggestionsDropdown.style.display = 'block';
            }
        }
        
        // Initialize suggestions on page load for even faster first focus
        if (popularQueries.length > 0) {
            suggestions = popularQueries.map(item => ({
                text: item.query,
                count: item.count,
                type: 'ranking'
            }));
            // Pre-render but keep hidden
            renderSuggestions();
            suggestionsDropdown.style.display = 'none';
        }
        
        // Disable dropdown on search results page when page loads with query
        if (searchInput.value.trim() !== '' && window.location.pathname === '/search') {
            shouldShowDropdownOnFocus = false;
            suggestionsDropdown.style.display = 'none';
        }
        
        // Keyboard navigation
        searchInput.addEventListener('keydown', function(e) {
            const items = suggestionsList.querySelectorAll('.suggestion-item');
            
            if (e.key === 'ArrowDown') {
                e.preventDefault();
                currentSuggestionIndex = Math.min(currentSuggestionIndex + 1, items.length - 1);
                updateSuggestionSelection();
            } else if (e.key === 'ArrowUp') {
                e.preventDefault();
                currentSuggestionIndex = Math.max(currentSuggestionIndex - 1, -1);
                updateSuggestionSelection();
            } else if (e.key === 'Enter') {
                e.preventDefault();
                if (currentSuggestionIndex >= 0 && items[currentSuggestionIndex]) {
                    const suggestionText = suggestions[currentSuggestionIndex].text;
                    selectSuggestion(suggestionText);
                    // Submit the form with the selected suggestion
                    if (validateAndSubmit(this.form)) {
                        this.form.submit();
                    }
                } else {
                    // Normal form submission
                    if (validateAndSubmit(this.form)) {
                        this.form.submit();
                    }
                }
            } else if (e.key === 'Escape') {
                suggestionsDropdown.style.display = 'none';
                currentSuggestionIndex = -1;
            }
        });
        
        // Click outside to close
        document.addEventListener('click', function(e) {
            if (!searchInput.contains(e.target) && !suggestionsDropdown.contains(e.target)) {
                suggestionsDropdown.style.display = 'none';
                currentSuggestionIndex = -1;
            }
        });
        
        // Prevent empty search submissions
        function validateAndSubmit(form) {
            const query = searchInput.value.trim();
            if (query === '') {
                // Visual feedback like Google - briefly highlight the input
                searchInput.classList.add('is-invalid');
                searchInput.focus();
                setTimeout(() => {
                    searchInput.classList.remove('is-invalid');
                }, 1500);
                return false; // Prevent submission like Google
            }
            return true;
        }
        
        // Handle form submission (button click)
        const searchForm = searchInput.closest('form');
        if (searchForm) {
            searchForm.addEventListener('submit', function(e) {
                if (!validateAndSubmit(this)) {
                    e.preventDefault();
                }
            });
        }
        
        searchInput.focus();
    }
    
    const resultItems = document.querySelectorAll('.result-item');
    resultItems.forEach(function(item) {
        item.addEventListener('click', function() {
            const link = this.querySelector('a');
            if (link) {
                window.open(link.href, '_blank');
            }
        });
    });
});