// Authentication module
app.auth = {
    // Login user
    async login(username) {
        if (!username || username.trim() === '') {
            app.utils.showAlert('ユーザー名を入力してください', 'danger');
            return false;
        }

        app.showLoading();

        try {
            const response = await fetch('/login', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/x-www-form-urlencoded',
                },
                body: new URLSearchParams({
                    username: username.trim()
                })
            });

            if (response.ok) {
                // Check if response is a redirect (successful login)
                if (response.redirected || response.url.includes('/')) {
                    app.state.user = username.trim();
                    localStorage.setItem('currentUser', username.trim());
                    app.updateUserDisplay();
                    app.router.navigate('home');
                    return true;
                }
            } else {
                const errorText = await response.text();
                app.utils.showAlert('ログインに失敗しました', 'danger');
            }
        } catch (error) {
            console.error('Login error:', error);
            app.utils.showAlert('ログイン中にエラーが発生しました', 'danger');
        } finally {
            app.hideLoading();
        }

        return false;
    },

    // Logout user
    async logout() {
        app.showLoading();

        try {
            const response = await fetch('/logout', {
                method: 'POST'
            });

            // Clear local state regardless of response
            app.state.user = null;
            localStorage.removeItem('currentUser');
            app.updateUserDisplay();
            app.router.navigate('login');
        } catch (error) {
            console.error('Logout error:', error);
            // Still clear local state on error
            app.state.user = null;
            localStorage.removeItem('currentUser');
            app.updateUserDisplay();
            app.router.navigate('login');
        } finally {
            app.hideLoading();
        }
    },

    // Check if user is authenticated
    isAuthenticated() {
        return !!app.state.user;
    },

    // Get current user
    getCurrentUser() {
        return app.state.user;
    }
};