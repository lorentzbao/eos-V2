// Router module for navigation
app.router = {
    // Current route
    currentRoute: null,

    // Navigate to a specific page
    navigate(page, params = {}) {
        console.log(`Navigating to: ${page}`, params);

        // Check authentication for protected pages
        if (page !== 'login' && !app.auth.isAuthenticated()) {
            this.navigate('login');
            return;
        }

        // Store current route
        this.currentRoute = { page, params };
        app.state.currentPage = page;

        // Update URL without page reload (but don't update for login page)
        if (page !== 'login') {
            const url = page === 'home' ? '/' : `/${page}`;
            window.history.pushState({ page, params }, '', url);
        }

        // Load the page content
        this.loadPage(page, params);
    },

    // Load page content
    async loadPage(page, params = {}) {
        console.log(`Loading page: ${page}`, params);
        app.showLoading();

        try {
            let content = '';
            let targetContainer;

            if (page === 'login') {
                targetContainer = document.getElementById('loginContent');
                console.log('Login container found:', !!targetContainer);
                content = app.pages.renderLoginPage();
                app.setPageTitle('ログイン - Enterprise Online Search');

                // Ensure login layout is visible
                const loginLayout = document.getElementById('loginLayout');
                const mainLayout = document.getElementById('mainLayout');
                if (loginLayout) loginLayout.style.display = 'flex';
                if (mainLayout) mainLayout.style.display = 'none';
            } else {
                targetContainer = document.getElementById('app-content');
                console.log('App content container found:', !!targetContainer);

                // Ensure main layout is visible
                const loginLayout = document.getElementById('loginLayout');
                const mainLayout = document.getElementById('mainLayout');
                if (loginLayout) loginLayout.style.display = 'none';
                if (mainLayout) mainLayout.style.display = 'flex';

                switch (page) {
                    case 'home':
                        content = await app.pages.renderHomePage();
                        app.setPageTitle('Enterprise Online Search');
                        break;

                    case 'search':
                        content = await app.pages.renderSearchPage(params);
                        app.setPageTitle('検索結果 - Enterprise Online Search');
                        break;

                    case 'history':
                        content = await app.pages.renderHistoryPage(params);
                        app.setPageTitle('検索履歴 - Enterprise Online Search');
                        break;

                    case 'rankings':
                        content = await app.pages.renderRankingsPage();
                        app.setPageTitle('検索ランキング - Enterprise Online Search');
                        break;

                    default:
                        content = '<div class="alert alert-danger">ページが見つかりません</div>';
                        app.setPageTitle('エラー - Enterprise Online Search');
                }
            }

            if (!targetContainer) {
                console.error('Target container not found for page:', page);
                return;
            }

            console.log('Setting content for page:', page);
            targetContainer.innerHTML = content;

            // Update active navigation
            if (page !== 'login') {
                app.updateActiveNav(page);
            }

            // Execute page-specific initialization
            this.initializePage(page, params);

        } catch (error) {
            console.error('Error loading page:', error);
            const fallbackContainer = document.getElementById('app-content') || document.getElementById('loginContent');
            if (fallbackContainer) {
                fallbackContainer.innerHTML = '<div class="alert alert-danger">ページの読み込みに失敗しました</div>';
            }
        } finally {
            app.hideLoading();
        }
    },

    // Initialize page-specific functionality
    initializePage(page, params) {
        switch (page) {
            case 'login':
                this.initLoginPage();
                break;

            case 'home':
                this.initHomePage();
                break;

            case 'search':
                this.initSearchPage(params);
                break;

            case 'history':
                this.initHistoryPage();
                break;

            case 'rankings':
                this.initRankingsPage();
                break;
        }
    },

    // Initialize login page
    initLoginPage() {
        const loginForm = document.getElementById('loginForm');
        if (loginForm) {
            loginForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                const username = document.getElementById('username').value;
                await app.auth.login(username);
            });

            // Focus on username input
            const usernameInput = document.getElementById('username');
            if (usernameInput) {
                usernameInput.focus();
            }
        }
    },

    // Initialize home page
    initHomePage() {
        const searchForm = document.getElementById('homeSearchForm');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const formData = new FormData(searchForm);

                // Validate form data before proceeding
                if (!app.forms.validateSearchForm(formData)) {
                    return;
                }

                const params = Object.fromEntries(formData.entries());
                this.navigate('search', params);
            });
        }

        // Initialize form handlers for conditional fields
        app.forms.initFormHandlers();

        // Initialize search suggestions
        app.search.initSearchSuggestions('searchInput');
    },

    // Initialize search page
    initSearchPage(params) {
        const searchForm = document.getElementById('searchForm');
        if (searchForm) {
            searchForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const formData = new FormData(searchForm);

                // Validate form data before proceeding
                if (!app.forms.validateSearchForm(formData)) {
                    return;
                }

                const newParams = Object.fromEntries(formData.entries());
                this.navigate('search', newParams);
            });
        }

        // Initialize form handlers for conditional fields
        app.forms.initFormHandlers();

        // Initialize search suggestions
        app.search.initSearchSuggestions('searchInput');

        // Initialize pagination if results exist
        if (params.results && params.results.length > 0) {
            app.pagination.init(params.results);
        }

        // Initialize CSV download
        app.csvDownload.init();

        // Initialize display options form if it exists
        const displayOptionsForm = document.getElementById('displayOptionsForm');
        if (displayOptionsForm) {
            displayOptionsForm.addEventListener('submit', (e) => {
                e.preventDefault();
                const formData = new FormData(displayOptionsForm);
                const newParams = Object.fromEntries(formData.entries());
                this.navigate('search', newParams);
            });
        }
    },

    // Initialize history page
    initHistoryPage() {
        // No specific initialization needed for history page
    },

    // Initialize rankings page
    initRankingsPage() {
        // No specific initialization needed for rankings page
    },

    // Handle browser back/forward buttons
    handlePopState(event) {
        if (event.state) {
            const { page, params } = event.state;
            this.currentRoute = { page, params };
            app.state.currentPage = page;
            this.loadPage(page, params);
        }
    },

    // Get current URL parameters
    getUrlParams() {
        const params = new URLSearchParams(window.location.search);
        return Object.fromEntries(params.entries());
    }
};

// Handle browser navigation
window.addEventListener('popstate', (event) => {
    app.router.handlePopState(event);
});