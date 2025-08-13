document.addEventListener('DOMContentLoaded', function() {
    const searchInput = document.querySelector('input[name="q"]');
    
    if (searchInput) {
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
        
        // Handle Enter key press
        searchInput.addEventListener('keypress', function(e) {
            if (e.key === 'Enter') {
                e.preventDefault();
                if (validateAndSubmit(this.form)) {
                    this.form.submit();
                }
            }
        });
        
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