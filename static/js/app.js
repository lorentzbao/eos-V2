// Main application module
window.app = {
    // Application state
    state: {
        user: null,
        currentPage: 'login',
        searchResults: null,
        popularQueries: []
    },

    // Application configuration
    config: {
        apiBase: '/api',
        pages: ['login', 'home', 'search', 'history', 'rankings']
    },

    // Initialize the application
    init() {
        console.log('Initializing Enterprise Online Search App...');

        // Check if user is already logged in
        const savedUser = localStorage.getItem('currentUser');
        if (savedUser) {
            this.state.user = savedUser;
            this.updateUserDisplay();
            this.router.navigate('home');
        } else {
            this.updateUserDisplay();
            this.router.navigate('login');
        }

        // Load popular queries
        this.loadPopularQueries();
    },

    // Show loading overlay
    showLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'flex';
        }
    },

    // Hide loading overlay
    hideLoading() {
        const overlay = document.getElementById('loadingOverlay');
        if (overlay) {
            overlay.style.display = 'none';
        }
    },

    // Update page title
    setPageTitle(title) {
        document.getElementById('pageTitle').textContent = title;
        document.title = title;
    },

    // Update username display and layout
    updateUserDisplay() {
        const usernameDisplay = document.getElementById('usernameDisplay');
        const headerUser = document.getElementById('headerUser');

        if (this.state.user && usernameDisplay) {
            usernameDisplay.textContent = this.state.user;
            if (headerUser) headerUser.style.display = 'flex';
        } else {
            if (headerUser) headerUser.style.display = 'none';
        }
    },

    // Update active navigation
    updateActiveNav(page) {
        // Remove active class from all nav links
        document.querySelectorAll('.sidebar .nav-link').forEach(link => {
            link.classList.remove('active');
        });

        // Add active class to current page nav link
        const activeNavId = {
            'home': 'nav-search',
            'search': 'nav-search',
            'rankings': 'nav-rankings',
            'history': 'nav-history'
        }[page];

        if (activeNavId) {
            const activeNav = document.getElementById(activeNavId);
            if (activeNav) {
                activeNav.classList.add('active');
            }
        }
    },

    // Load popular queries from backend
    async loadPopularQueries() {
        try {
            const response = await fetch('/api/popular-queries');
            if (response.ok) {
                this.state.popularQueries = await response.json();
            }
        } catch (error) {
            console.error('Failed to load popular queries:', error);
        }
    },

    // Update popular queries incrementally in memory
    updatePopularQueriesIncremental(newQuery) {
        if (!newQuery || !newQuery.trim()) {
            return;
        }

        const query = newQuery.trim();
        const existing = this.state.popularQueries.find(q => q.query === query);

        if (existing) {
            // Increment count for existing query
            existing.count++;
        } else {
            // Add new query with count 1
            this.state.popularQueries.push({
                query: query,
                count: 1
            });
        }

        // Re-sort by count (descending) and limit to top 10
        this.state.popularQueries.sort((a, b) => b.count - a.count);
        if (this.state.popularQueries.length > 10) {
            this.state.popularQueries = this.state.popularQueries.slice(0, 10);
        }
    },

    // Utility functions
    utils: {
        // Format date
        formatDate(dateString) {
            const date = new Date(dateString);
            return date.toLocaleString('ja-JP');
        },

        // Escape HTML
        escapeHtml(text) {
            const div = document.createElement('div');
            div.textContent = text;
            return div.innerHTML;
        },

        // Show alert message
        showAlert(message, type = 'info', container = '#app-content') {
            const alertDiv = document.createElement('div');
            alertDiv.className = `alert alert-${type} alert-dismissible fade show mt-2`;
            alertDiv.innerHTML = `
                ${message}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            `;

            const targetContainer = document.querySelector(container);
            if (targetContainer) {
                targetContainer.insertBefore(alertDiv, targetContainer.firstChild);

                // Auto-hide after 5 seconds
                setTimeout(() => {
                    if (alertDiv.parentNode) {
                        alertDiv.remove();
                    }
                }, 5000);
            }
        },

        // Debounce function
        debounce(func, wait) {
            let timeout;
            return function executedFunction(...args) {
                const later = () => {
                    clearTimeout(timeout);
                    func(...args);
                };
                clearTimeout(timeout);
                timeout = setTimeout(later, wait);
            };
        }
    },

    // Form handling functionality
    forms: {
        // Initialize form event listeners
        initFormHandlers() {
            // Handle target selection changes
            const targetRadios = document.querySelectorAll('input[name="target"]');
            targetRadios.forEach(radio => {
                radio.addEventListener('change', this.handleTargetChange);
            });

            // Handle prefecture selection changes to load cities
            const prefectureSelects = document.querySelectorAll('select[name="prefecture"]');
            prefectureSelects.forEach(select => {
                select.addEventListener('change', async (e) => {
                    await app.forms.loadCities(e.target.value);
                });
            });
        },

        // Load cities for selected prefecture
        async loadCities(prefecture) {
            if (!prefecture) {
                // Clear city dropdown if no prefecture selected
                const citySelects = document.querySelectorAll('select[name="city"]');
                citySelects.forEach(select => {
                    select.innerHTML = '<option value="">市区町村を選択（任意）</option>';
                    select.disabled = true;
                });
                return;
            }

            try {
                const response = await fetch(`/api/cities/${prefecture}`);
                if (!response.ok) {
                    throw new Error('Failed to load cities');
                }

                const data = await response.json();
                const cities = data.cities || [];

                // Update all city dropdowns
                const citySelects = document.querySelectorAll('select[name="city"]');
                citySelects.forEach(select => {
                    select.innerHTML = '<option value="">市区町村を選択（任意）</option>';

                    cities.forEach(city => {
                        const option = document.createElement('option');
                        option.value = city.value;
                        option.textContent = city.name;
                        select.appendChild(option);
                    });

                    select.disabled = false;
                });

            } catch (error) {
                console.error('Error loading cities:', error);
                app.utils.showAlert('市区町村の読み込みに失敗しました。', 'warning');
            }
        },

        // Handle target selection change
        handleTargetChange(event) {
            const selectedTarget = event.target.value;
            const shirachiFields = document.getElementById('shirachi-fields');
            const keiyakuFields = document.getElementById('keiyaku-fields');

            // Hide all conditional fields first
            if (shirachiFields) shirachiFields.style.display = 'none';
            if (keiyakuFields) keiyakuFields.style.display = 'none';

            // Clear form validation for hidden fields
            app.forms.clearFieldValidation();

            // Show appropriate fields based on selection
            if (selectedTarget === '白地・過去' && shirachiFields) {
                shirachiFields.style.display = 'block';
                // Make prefecture required for 白地・過去
                const prefectureSelect = shirachiFields.querySelector('select[name="prefecture"]');
                if (prefectureSelect) {
                    prefectureSelect.setAttribute('required', 'true');
                }
            } else if (selectedTarget === '契約' && keiyakuFields) {
                keiyakuFields.style.display = 'block';
                // Make regional office required for 契約
                const regionalOfficeSelect = keiyakuFields.querySelector('select[name="regional_office"]');
                if (regionalOfficeSelect) {
                    regionalOfficeSelect.setAttribute('required', 'true');
                }
            }
        },

        // Clear field validation states
        clearFieldValidation() {
            // Remove required attribute from all conditional fields
            document.querySelectorAll('.conditional-fields select').forEach(select => {
                select.removeAttribute('required');
                select.classList.remove('is-invalid');
            });
        },

        // Validate form before submission
        validateSearchForm(formData) {
            const target = formData.get('target');

            if (!target) {
                app.utils.showAlert('対象を選択してください。', 'danger');
                return false;
            }

            if (target === '白地・過去') {
                const prefecture = formData.get('prefecture');
                if (!prefecture) {
                    app.utils.showAlert('都道府県を選択してください。', 'danger');
                    return false;
                }
            } else if (target === '契約') {
                const regionalOffice = formData.get('regional_office');
                if (!regionalOffice) {
                    app.utils.showAlert('地域事業本部を選択してください。', 'danger');
                    return false;
                }
            }

            return true;
        }
    }
};