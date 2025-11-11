// CSV Download module
app.csvDownload = {
    // Initialize CSV download functionality
    init() {
        const downloadBtn = document.getElementById('downloadBtn');
        if (!downloadBtn) return;

        downloadBtn.addEventListener('click', () => {
            this.downloadCSV();
        });
    },

    // Download CSV file
    async downloadCSV() {
        const downloadBtn = document.getElementById('downloadBtn');
        if (!downloadBtn) return;

        const originalHTML = downloadBtn.innerHTML;

        try {
            // Show loading state
            downloadBtn.innerHTML = '<span class="spinner-border spinner-border-sm me-1"></span> Preparing CSV...';
            downloadBtn.disabled = true;

            // Get current search parameters from the URL or form
            const searchParams = this.getCurrentSearchParams();

            // Build download URL
            const downloadUrl = `/api/download-csv?${searchParams.toString()}`;

            // Use fetch to handle both file and JSON responses
            const response = await fetch(downloadUrl);

            // Check content type to determine if it's a file or JSON
            const contentType = response.headers.get('content-type');

            if (contentType && contentType.includes('application/json')) {
                // Handle JSON response (when browser download is disabled)
                const data = await response.json();
                if (data.success) {
                    // Show the message to user
                    app.utils.showAlert(data.message, 'info');
                } else {
                    app.utils.showAlert('CSVダウンロード中にエラーが発生しました', 'danger');
                }
            } else {
                // Handle file download response
                const blob = await response.blob();
                const url = window.URL.createObjectURL(blob);

                // Create temporary download link
                const link = document.createElement('a');
                link.href = url;

                // Extract filename from Content-Disposition header
                const contentDisposition = response.headers.get('content-disposition');
                let filename = 'search_results.csv';
                if (contentDisposition) {
                    const filenameMatch = contentDisposition.match(/filename="?(.+)"?/);
                    if (filenameMatch) {
                        filename = filenameMatch[1];
                    }
                }
                link.download = filename;
                link.style.display = 'none';

                document.body.appendChild(link);
                link.click();
                document.body.removeChild(link);

                // Clean up blob URL
                window.URL.revokeObjectURL(url);

                // Show success message
                this.showDownloadSuccess();
            }

        } catch (error) {
            console.error('CSV download error:', error);
            app.utils.showAlert('CSVダウンロード中にエラーが発生しました', 'danger');
        } finally {
            // Reset button after delay
            setTimeout(() => {
                downloadBtn.innerHTML = originalHTML;
                downloadBtn.disabled = false;
            }, 3000);
        }
    },

    // Get current search parameters
    getCurrentSearchParams() {
        // Try to get parameters from current route
        if (app.router.currentRoute && app.router.currentRoute.params) {
            return new URLSearchParams(app.router.currentRoute.params);
        }

        // Fallback: try to get from form if available
        const searchForm = document.getElementById('searchForm');
        if (searchForm) {
            const formData = new FormData(searchForm);
            return new URLSearchParams(formData);
        }

        // Fallback: get from URL
        return new URLSearchParams(window.location.search);
    },

    // Show download success message
    showDownloadSuccess() {
        const alertDiv = document.createElement('div');
        alertDiv.className = 'alert alert-success alert-dismissible fade show mt-2';
        alertDiv.innerHTML = `
            <small>
                <strong>📥 ダウンロード開始!</strong>
                CSVファイルのダウンロードが開始されました。
            </small>
            <button type="button" class="btn-close btn-close-sm" data-bs-dismiss="alert"></button>
        `;

        // Insert after stats section
        const statsSection = document.querySelector('.mt-5');
        if (statsSection && statsSection.parentNode) {
            statsSection.parentNode.insertBefore(alertDiv, statsSection.nextSibling);
        } else {
            // Fallback: insert at the beginning of app content
            const appContent = document.getElementById('app-content');
            if (appContent) {
                appContent.insertBefore(alertDiv, appContent.firstChild);
            }
        }

        // Auto-hide after 3 seconds
        setTimeout(() => {
            if (alertDiv.parentNode) {
                alertDiv.remove();
            }
        }, 3000);
    }
};