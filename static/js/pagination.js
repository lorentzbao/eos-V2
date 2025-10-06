// Pagination module
app.pagination = {
    // Pagination state
    currentPage: 1,
    itemsPerPage: 10,
    totalItems: 0,

    // Initialize pagination
    init(results = null) {
        const resultItems = document.querySelectorAll('.result-item');
        this.totalItems = resultItems.length;

        if (this.totalItems > this.itemsPerPage) {
            const paginationNav = document.getElementById('pagination');
            if (paginationNav) {
                paginationNav.style.display = 'block';
            }
            this.showPage(1);
        }
    },

    // Show specific page
    showPage(page) {
        this.currentPage = page;
        const startIndex = (page - 1) * this.itemsPerPage;
        const endIndex = startIndex + this.itemsPerPage;

        // Show/hide result items for current page
        const resultItems = document.querySelectorAll('.result-item');
        resultItems.forEach((item, index) => {
            item.style.display = (index >= startIndex && index < endIndex) ? 'block' : 'none';
        });

        // Update pagination info
        this.updatePaginationInfo();

        // Generate pagination buttons
        this.generatePaginationButtons();

        // Scroll to top of results
        const searchResults = document.getElementById('searchResults');
        if (searchResults) {
            searchResults.scrollIntoView({ behavior: 'smooth', block: 'start' });
        }
    },

    // Update pagination information display
    updatePaginationInfo() {
        const totalPages = Math.ceil(this.totalItems / this.itemsPerPage);
        const showingStart = (this.currentPage - 1) * this.itemsPerPage + 1;
        const showingEnd = Math.min(this.currentPage * this.itemsPerPage, this.totalItems);

        const paginationInfo = document.getElementById('pagination-info');
        if (paginationInfo) {
            paginationInfo.textContent =
                `${showingStart}-${showingEnd} / ${this.totalItems} 社を表示 (ページ ${this.currentPage} / ${totalPages})`;
        }
    },

    // Generate pagination buttons
    generatePaginationButtons() {
        const paginationContainer = document.getElementById('pagination-buttons');
        if (!paginationContainer) return;

        paginationContainer.innerHTML = '';

        const totalPages = Math.ceil(this.totalItems / this.itemsPerPage);

        // Previous button
        const prevLi = document.createElement('li');
        prevLi.className = `page-item ${this.currentPage === 1 ? 'disabled' : ''}`;
        prevLi.innerHTML = `<a class="page-link" href="#" onclick="app.pagination.changePage(-1)">前へ</a>`;
        paginationContainer.appendChild(prevLi);

        // Calculate which page numbers to show
        let startPage = Math.max(1, this.currentPage - 2);
        let endPage = Math.min(totalPages, this.currentPage + 2);

        // Show first page if not in range
        if (startPage > 1) {
            const firstLi = document.createElement('li');
            firstLi.className = 'page-item';
            firstLi.innerHTML = `<a class="page-link" href="#" onclick="app.pagination.goToPage(1)">1</a>`;
            paginationContainer.appendChild(firstLi);

            if (startPage > 2) {
                const dotsLi = document.createElement('li');
                dotsLi.className = 'page-item disabled';
                dotsLi.innerHTML = '<span class="page-link">...</span>';
                paginationContainer.appendChild(dotsLi);
            }
        }

        // Show page numbers
        for (let i = startPage; i <= endPage; i++) {
            const pageLi = document.createElement('li');
            pageLi.className = `page-item ${i === this.currentPage ? 'active' : ''}`;
            pageLi.innerHTML = `<a class="page-link" href="#" onclick="app.pagination.goToPage(${i})">${i}</a>`;
            paginationContainer.appendChild(pageLi);
        }

        // Show last page if not in range
        if (endPage < totalPages) {
            if (endPage < totalPages - 1) {
                const dotsLi = document.createElement('li');
                dotsLi.className = 'page-item disabled';
                dotsLi.innerHTML = '<span class="page-link">...</span>';
                paginationContainer.appendChild(dotsLi);
            }

            const lastLi = document.createElement('li');
            lastLi.className = 'page-item';
            lastLi.innerHTML = `<a class="page-link" href="#" onclick="app.pagination.goToPage(${totalPages})">${totalPages}</a>`;
            paginationContainer.appendChild(lastLi);
        }

        // Next button
        const nextLi = document.createElement('li');
        nextLi.className = `page-item ${this.currentPage === totalPages ? 'disabled' : ''}`;
        nextLi.innerHTML = `<a class="page-link" href="#" onclick="app.pagination.changePage(1)">次へ</a>`;
        paginationContainer.appendChild(nextLi);
    },

    // Change page by direction (-1 for previous, 1 for next)
    changePage(direction) {
        const totalPages = Math.ceil(this.totalItems / this.itemsPerPage);
        const newPage = this.currentPage + direction;

        if (newPage >= 1 && newPage <= totalPages) {
            this.showPage(newPage);
        }
    },

    // Go to specific page
    goToPage(page) {
        const totalPages = Math.ceil(this.totalItems / this.itemsPerPage);
        if (page >= 1 && page <= totalPages) {
            this.showPage(page);
        }
    },

    // Reset pagination
    reset() {
        this.currentPage = 1;
        this.totalItems = 0;

        const paginationNav = document.getElementById('pagination');
        if (paginationNav) {
            paginationNav.style.display = 'none';
        }
    }
};