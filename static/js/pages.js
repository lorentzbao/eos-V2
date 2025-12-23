// Page rendering module
app.pages = {
    // Prefecture data cache
    _prefectureData: null,
    // Contract data cache
    _contractData: null,

    // Load prefecture data from API
    async loadPrefectures() {
        if (this._prefectureData) {
            return this._prefectureData;
        }

        try {
            const response = await fetch('/api/prefectures');
            const data = await response.json();
            this._prefectureData = data.prefectures || [];
            return this._prefectureData;
        } catch (error) {
            console.error('Failed to load prefectures:', error);
            return [];
        }
    },

    // Load contract data from API (districts, branches, solicitors)
    async loadContractData() {
        if (this._contractData) {
            return this._contractData;
        }

        try {
            const response = await fetch('/api/contract-data');
            const data = await response.json();
            this._contractData = data.data || {};
            return this._contractData;
        } catch (error) {
            console.error('Failed to load contract data:', error);
            return {};
        }
    },

    // Generate prefecture options HTML
    getPrefectureOptions(selectedValue = '') {
        if (!this._prefectureData) {
            // Return empty if data not loaded yet
            return '';
        }

        return this._prefectureData.map(pref => {
            const selected = pref.value === selectedValue ? 'selected' : '';
            return `<option value="${pref.value}" ${selected}>${pref.name}</option>`;
        }).join('\n');
    },

    // Generate district options HTML
    getDistrictOptions(selectedValue = '') {
        if (!this._contractData) {
            return '';
        }

        const districts = Object.keys(this._contractData).map(key => ({
            value: key,
            name: this._contractData[key].name
        }));

        return districts.map(district => {
            const selected = district.value === selectedValue ? 'selected' : '';
            return `<option value="${district.value}" ${selected}>${district.name}</option>`;
        }).join('\n');
    },

    // Generate branch options HTML for a specific district
    getBranchOptions(districtCode, selectedValue = '') {
        if (!this._contractData || !districtCode) {
            return '';
        }

        const district = this._contractData[districtCode];
        if (!district || !district.branches) {
            return '';
        }

        return district.branches.map(branch => {
            const selected = branch.code === selectedValue ? 'selected' : '';
            return `<option value="${branch.code}" ${selected}>${branch.name}</option>`;
        }).join('\n');
    },

    // Generate solicitor options HTML for a specific district and branch
    getSolicitorOptions(districtCode, branchCode, selectedValue = '') {
        if (!this._contractData || !districtCode || !branchCode) {
            return '';
        }

        const district = this._contractData[districtCode];
        if (!district || !district.branches) {
            return '';
        }

        const branch = district.branches.find(b => b.code === branchCode);
        if (!branch || !branch.solicitors) {
            return '';
        }

        return branch.solicitors.map(solicitor => {
            const selected = solicitor.code === selectedValue ? 'selected' : '';
            return `<option value="${solicitor.code}" ${selected}>${solicitor.name}</option>`;
        }).join('\n');
    },

    // Render login page
    renderLoginPage() {
        return `
            <div class="login-container">
                <div class="text-center mb-4">
                    <h2 class="display-6 mb-3">Enterprise Online Search</h2>
                    <p class="lead">ログインして検索を開始</p>
                </div>

                <div class="content-container">
                    <div class="text-center mb-4">
                        <h4 class="mb-0" style="color: var(--primary-dark);">🔐 ログイン</h4>
                    </div>

                    <form id="loginForm">
                        <div class="mb-3">
                            <label for="username" class="form-label">LANID</label>
                            <input type="text"
                                   class="form-control"
                                   id="username"
                                   name="username"
                                   placeholder="LANIDを入力してください"
                                   required>
                        </div>

                        <div class="d-grid">
                            <button type="submit" class="btn btn-primary-eos">ログイン</button>
                        </div>
                    </form>

                    <div class="login-info mt-4">
                        <div class="d-flex align-items-start">
                            <i class="text-info me-2">ℹ️</i>
                            <small>
                                <strong>注意:</strong> このシステムはLANIDのみを記録し、パスワードは必要ありません。
                                検索履歴を追跡するために使用されます。
                            </small>
                        </div>
                    </div>

                    <div class="mt-3 text-center">
                        <a href="https://forms.office.com/pages/responsepage.aspx?id=test"
                           target="_blank"
                           class="btn btn-outline-secondary">
                            ユーザー登録
                        </a>
                    </div>
                </div>
            </div>
        `;
    },

    // Render home page
    async renderHomePage() {
        return `
            <div class="row">
                <div class="col-md-12">
                    <div class="search-container">
                        <form id="homeSearchForm">
                            <!-- Search Criteria Section -->
                            <div class="search-criteria mb-4">
                                <h6 class="mb-3" style="color: var(--primary-dark);">検索条件</h6>

                                <!-- Target Selection (Required) -->
                                <div class="row g-3 mb-3">
                                    <div class="col-md-12">
                                        <label class="form-label fw-bold">対象 <span class="text-danger">*</span></label>
                                        <div class="btn-group w-100" role="group" id="targetSelection">
                                            <input type="radio" class="btn-check" name="target" id="target-shirachi" value="白地・過去" checked required>
                                            <label class="btn btn-outline-primary" for="target-shirachi">白地・過去</label>

                                            <input type="radio" class="btn-check" name="target" id="target-keiyaku" value="契約" required>
                                            <label class="btn btn-outline-primary" for="target-keiyaku">契約</label>
                                        </div>
                                    </div>
                                </div>

                                <!-- Conditional Fields for 白地・過去 -->
                                <div id="shirachi-fields" class="conditional-fields" style="display: block;">
                                    <div class="row g-3">
                                        <div class="col-md-6">
                                            <label class="form-label">都道府県 <span class="text-danger">*</span></label>
                                            <select name="prefecture" class="form-select">
                                                <option value="">都道府県を選択</option>
                                                ${this.getPrefectureOptions()}
                                            </select>
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label">市区町村</label>
                                            <select name="city" class="form-select" disabled>
                                                <option value="">市区町村を選択（任意）</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>

                                <!-- Conditional Fields for 契約 -->
                                <div id="keiyaku-fields" class="conditional-fields" style="display: none;">
                                    <div class="row g-3">
                                        <div class="col-md-4">
                                            <label class="form-label">地域事業本部 <span class="text-danger">*</span></label>
                                            <select name="regional_office" id="district-select" class="form-select">
                                                <option value="">地域事業本部を選択</option>
                                                ${this.getDistrictOptions()}
                                            </select>
                                        </div>
                                        <div class="col-md-4">
                                            <label class="form-label">支店</label>
                                            <select name="branch" id="branch-select" class="form-select" disabled>
                                                <option value="">支店を選択（任意）</option>
                                            </select>
                                        </div>
                                        <div class="col-md-4">
                                            <label class="form-label">ソリシター</label>
                                            <select name="solicitor" id="solicitor-select" class="form-select" disabled>
                                                <option value="">ソリシターを選択（任意）</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Search Input -->
                            <div class="input-group mb-3 position-relative">
                                <input type="text"
                                       id="searchInput"
                                       name="q"
                                       class="form-control form-control-lg"
                                       placeholder="検索キーワードを入力してください..."
                                       autocomplete="off"
                                       required
                                       autofocus>
                                <button class="btn btn-primary btn-lg" type="submit">検索</button>

                                <!-- Search suggestions dropdown -->
                                <div id="searchSuggestions" class="suggestions-dropdown" style="display: none;">
                                    <div class="suggestions-header">
                                        <small class="text-muted">🏆 人気の検索キーワード</small>
                                    </div>
                                    <div id="suggestionsList"></div>
                                </div>
                            </div>

                            <!-- Hidden inputs for defaults -->
                            <input type="hidden" name="limit" value="${app.config.searchDefaultLimit}">
                            <input type="hidden" name="search_option" value="all">
                        </form>
                    </div>

                    <div class="mt-5">
                        <div class="card border-0 bg-light">
                            <div class="card-body">
                                <h6 class="card-title text-muted mb-3">💡 検索のヒント</h6>
                                <div class="row">
                                    <div class="col-md-6 mb-3">
                                        <ul class="list-unstyled mb-0">
                                            <li class="mb-2">
                                                <small class="text-muted">
                                                    <strong>🎯 対象選択：</strong>「白地・過去」または「契約」を選択してください
                                                </small>
                                            </li>
                                            <li class="mb-2">
                                                <small class="text-muted">
                                                    <strong>🏢 白地・過去：</strong>都道府県の選択が必須です
                                                </small>
                                            </li>
                                            <li class="mb-2">
                                                <small class="text-muted">
                                                    <strong>📋 契約：</strong>地域事業本部の選択が必須です
                                                </small>
                                            </li>
                                        </ul>
                                    </div>
                                    <div class="col-md-6 mb-3">
                                        <ul class="list-unstyled mb-0">
                                            <li class="mb-2">
                                                <small class="text-muted">
                                                    <strong>🔍 キーワード：</strong>企業名や業種名で検索できます
                                                </small>
                                            </li>
                                            <li class="mb-2">
                                                <small class="text-muted">
                                                    <strong>⚙️ 表示オプション：</strong>検索後にマッチ方式を変更できます
                                                </small>
                                            </li>
                                            <li class="mb-2">
                                                <small class="text-muted">
                                                    <strong>📥 リスト作成：</strong>検索結果をCSVファイルでダウンロードできます
                                                </small>
                                            </li>
                                        </ul>
                                    </div>
                                </div>
                            </div>
                        </div>
                    </div>
                </div>
            </div>
        `;
    },

    // Render search page
    async renderSearchPage(params = {}) {
        try {
            // If we have search parameters, perform the search
            if (params.q) {
                const data = await app.search.performSearch(params);
                return this.renderSearchResults(data, params);
            } else {
                // Show empty search page
                return this.renderSearchResults(null, params);
            }

        } catch (error) {
            console.error('[DEBUG] renderSearchPage caught error:', error);
            console.error('[DEBUG] Error type:', typeof error);
            console.error('[DEBUG] Error message:', error.message);
            console.error('[DEBUG] Error object:', JSON.stringify(error, Object.getOwnPropertyNames(error)));
            const errorMessage = error.message || '不明なエラーが発生しました';
            console.log('[DEBUG] Final error message to display:', errorMessage);
            return `
                <div class="alert alert-danger">
                    <h5>検索エラー</h5>
                    <p>${app.utils.escapeHtml(errorMessage)}</p>
                    <p class="mb-0"><small>詳細はブラウザのコンソールをご確認ください。</small></p>
                </div>
            `;
        }
    },

    // Render search results
    renderSearchResults(data, params) {
        if (!data) {
            // Show empty search form
            return this.renderEmptySearchPage(params);
        }

        const { grouped_results, total_found, total_companies, search_time, processed_query, stats, cache_hit } = data;

        let content = `
            <div class="row">
                <div class="col-md-12">
                    <!-- Search Form -->
                    <div class="search-header mb-4">
                        <form id="searchForm">
                            <!-- Search Criteria Section -->
                            <div class="search-criteria mb-4">
                                <h6 class="mb-3" style="color: var(--primary-dark);">検索条件</h6>

                                <!-- Target Selection (Required) -->
                                <div class="row g-3 mb-3">
                                    <div class="col-md-12">
                                        <label class="form-label fw-bold">対象 <span class="text-danger">*</span></label>
                                        <div class="btn-group w-100" role="group" id="targetSelection">
                                            <input type="radio" class="btn-check" name="target" id="target-shirachi-search" value="白地・過去" ${params.target ? (params.target === '白地・過去' ? 'checked' : '') : 'checked'} required>
                                            <label class="btn btn-outline-primary" for="target-shirachi-search">白地・過去</label>

                                            <input type="radio" class="btn-check" name="target" id="target-keiyaku-search" value="契約" ${params.target === '契約' ? 'checked' : ''} required>
                                            <label class="btn btn-outline-primary" for="target-keiyaku-search">契約</label>
                                        </div>
                                    </div>
                                </div>

                                <!-- Conditional Fields for 白地・過去 -->
                                <div id="shirachi-fields" class="conditional-fields" style="display: ${!params.target || params.target === '白地・過去' ? 'block' : 'none'};">
                                    <div class="row g-3">
                                        <div class="col-md-6">
                                            <label class="form-label">都道府県 <span class="text-danger">*</span></label>
                                            <select name="prefecture" class="form-select" ${params.target === '白地・過去' ? 'required' : ''}>
                                                <option value="">都道府県を選択</option>
                                                ${this.getPrefectureOptions(params.prefecture)}
                                            </select>
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label">市区町村</label>
                                            <select name="city" class="form-select">
                                                <option value="">市区町村を選択（任意）</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>

                                <!-- Conditional Fields for 契約 -->
                                <div id="keiyaku-fields" class="conditional-fields" style="display: ${params.target === '契約' ? 'block' : 'none'};">
                                    <div class="row g-3">
                                        <div class="col-md-4">
                                            <label class="form-label">地域事業本部 <span class="text-danger">*</span></label>
                                            <select name="regional_office" class="contract-district-select form-select" ${params.target === '契約' ? 'required' : ''}>
                                                <option value="">地域事業本部を選択</option>
                                                ${this.getDistrictOptions(params.regional_office || '')}
                                            </select>
                                        </div>
                                        <div class="col-md-4">
                                            <label class="form-label">支店</label>
                                            <select name="branch" class="contract-branch-select form-select" ${!params.regional_office ? 'disabled' : ''}>
                                                <option value="">支店を選択（任意）</option>
                                                ${params.regional_office ? this.getBranchOptions(params.regional_office, params.branch || '') : ''}
                                            </select>
                                        </div>
                                        <div class="col-md-4">
                                            <label class="form-label">ソリシター</label>
                                            <select name="solicitor" class="contract-solicitor-select form-select" ${!params.branch ? 'disabled' : ''}>
                                                <option value="">ソリシターを選択（任意）</option>
                                                ${params.regional_office && params.branch ? this.getSolicitorOptions(params.regional_office, params.branch, params.solicitor || '') : ''}
                                            </select>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Search Input -->
                            <div class="input-group mb-3 position-relative">
                                <input type="text"
                                       id="searchInput"
                                       name="q"
                                       value="${app.utils.escapeHtml(params.q || '')}"
                                       class="form-control"
                                       placeholder="検索キーワードを入力してください..."
                                       autocomplete="off"
                                       required>
                                <button class="btn btn-primary" type="submit">検索</button>

                                <!-- Search suggestions dropdown -->
                                <div id="searchSuggestions" class="suggestions-dropdown" style="display: none;">
                                    <div class="suggestions-header">
                                        <small class="text-muted">🏆 人気の検索キーワード</small>
                                    </div>
                                    <div id="suggestionsList"></div>
                                </div>
                            </div>

                            <!-- Hidden inputs for defaults -->
                            <input type="hidden" name="limit" value="${params.limit || app.config.searchDefaultLimit}">
                            <input type="hidden" name="search_option" value="${params.search_option || 'all'}">
                        </form>
                    </div>


                    <!-- Search Stats -->
                    ${params.q ? `
                    <div class="search-stats mb-3">
                        <div class="d-flex justify-content-between align-items-start mb-1">
                            <small class="text-muted">
                                "${app.utils.escapeHtml(params.q)}" の検索結果${params.prefecture ? ` (${params.prefecture})` : ''}
                            </small>
                            <small class="text-muted">💡 最初の${params.limit || app.config.searchDefaultLimit}件のみ表示しております</small>
                        </div>
                        <div class="d-flex align-items-center gap-2 flex-wrap">
                            <span class="badge bg-primary">${total_found}件</span>
                            <span class="badge bg-secondary">${total_companies}社</span>
                            <small class="text-muted">${search_time}秒${cache_hit ? ' • キャッシュ' : ''}</small>
                        </div>
                    </div>
                    ` : ''}

                    <!-- Search Results -->
                    ${grouped_results && grouped_results.length > 0 ? `
                    <div class="search-results" id="searchResults">
                        ${grouped_results.map(company => this.renderCompanyResult(company)).join('')}
                    </div>
                    ` : params.q ? `
                    <div class="alert alert-info">
                        <h5>検索結果が見つかりませんでした</h5>
                        <p>以下をお試しください:</p>
                        <ul>
                            <li>キーワードのスペルを確認してください</li>
                            <li>別のキーワードで検索してみてください</li>
                            <li>より一般的な用語を使用してください</li>
                        </ul>
                    </div>
                    ` : ''}

                    <!-- Stats -->
                    ${stats ? `
                    <div class="mt-5">
                        <hr>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                インデックス済み文書数: ${stats.total_documents} 件
                            </small>
                            <div class="d-flex gap-2">
                                ${grouped_results && grouped_results.length > 0 ? `
                                <button id="downloadBtn" class="btn btn-sm btn-primary-dark">
                                    📥 リスト作成
                                </button>
                                ` : ''}
                            </div>
                        </div>
                    </div>
                    ` : ''}
                </div>
            </div>
        `;

        return content;
    },

    // Render empty search page
    renderEmptySearchPage(params) {
        return `
            <div class="row">
                <div class="col-md-12">
                    <!-- Search Form -->
                    <div class="search-header mb-4">
                        <form id="searchForm">
                            <!-- Search Criteria Section -->
                            <div class="search-criteria mb-4">
                                <h6 class="mb-3" style="color: var(--primary-dark);">検索条件</h6>

                                <!-- Target Selection (Required) -->
                                <div class="row g-3 mb-3">
                                    <div class="col-md-12">
                                        <label class="form-label fw-bold">対象 <span class="text-danger">*</span></label>
                                        <div class="btn-group w-100" role="group" id="targetSelection">
                                            <input type="radio" class="btn-check" name="target" id="target-shirachi-empty" value="白地・過去" ${params.target ? (params.target === '白地・過去' ? 'checked' : '') : 'checked'} required>
                                            <label class="btn btn-outline-primary" for="target-shirachi-empty">白地・過去</label>

                                            <input type="radio" class="btn-check" name="target" id="target-keiyaku-empty" value="契約" ${params.target === '契約' ? 'checked' : ''} required>
                                            <label class="btn btn-outline-primary" for="target-keiyaku-empty">契約</label>
                                        </div>
                                    </div>
                                </div>

                                <!-- Conditional Fields for 白地・過去 -->
                                <div id="shirachi-fields" class="conditional-fields" style="display: ${!params.target || params.target === '白地・過去' ? 'block' : 'none'};">
                                    <div class="row g-3">
                                        <div class="col-md-6">
                                            <label class="form-label">都道府県 <span class="text-danger">*</span></label>
                                            <select name="prefecture" class="form-select" ${params.target === '白地・過去' ? 'required' : ''}>
                                                <option value="">都道府県を選択</option>
                                                ${this.getPrefectureOptions(params.prefecture)}
                                            </select>
                                        </div>
                                        <div class="col-md-6">
                                            <label class="form-label">市区町村</label>
                                            <select name="city" class="form-select">
                                                <option value="">市区町村を選択（任意）</option>
                                            </select>
                                        </div>
                                    </div>
                                </div>

                                <!-- Conditional Fields for 契約 -->
                                <div id="keiyaku-fields" class="conditional-fields" style="display: ${params.target === '契約' ? 'block' : 'none'};">
                                    <div class="row g-3">
                                        <div class="col-md-4">
                                            <label class="form-label">地域事業本部 <span class="text-danger">*</span></label>
                                            <select name="regional_office" class="contract-district-select form-select" ${params.target === '契約' ? 'required' : ''}>
                                                <option value="">地域事業本部を選択</option>
                                                ${this.getDistrictOptions(params.regional_office || '')}
                                            </select>
                                        </div>
                                        <div class="col-md-4">
                                            <label class="form-label">支店</label>
                                            <select name="branch" class="contract-branch-select form-select" ${!params.regional_office ? 'disabled' : ''}>
                                                <option value="">支店を選択（任意）</option>
                                                ${params.regional_office ? this.getBranchOptions(params.regional_office, params.branch || '') : ''}
                                            </select>
                                        </div>
                                        <div class="col-md-4">
                                            <label class="form-label">ソリシター</label>
                                            <select name="solicitor" class="contract-solicitor-select form-select" ${!params.branch ? 'disabled' : ''}>
                                                <option value="">ソリシターを選択（任意）</option>
                                                ${params.regional_office && params.branch ? this.getSolicitorOptions(params.regional_office, params.branch, params.solicitor || '') : ''}
                                            </select>
                                        </div>
                                    </div>
                                </div>
                            </div>

                            <!-- Search Input -->
                            <div class="input-group mb-3 position-relative">
                                <input type="text"
                                       id="searchInput"
                                       name="q"
                                       value="${app.utils.escapeHtml(params.q || '')}"
                                       class="form-control"
                                       placeholder="検索キーワードを入力してください..."
                                       autocomplete="off"
                                       required>
                                <button class="btn btn-primary" type="submit">検索</button>

                                <!-- Search suggestions dropdown -->
                                <div id="searchSuggestions" class="suggestions-dropdown" style="display: none;">
                                    <div class="suggestions-header">
                                        <small class="text-muted">🏆 人気の検索キーワード</small>
                                    </div>
                                    <div id="suggestionsList"></div>
                                </div>
                            </div>

                            <!-- Hidden inputs for defaults -->
                            <input type="hidden" name="limit" value="${params.limit || app.config.searchDefaultLimit}">
                            <input type="hidden" name="search_option" value="${params.search_option || 'all'}">
                        </form>
                    </div>

                    <div class="alert alert-info">
                        <h5>検索を開始してください</h5>
                        <p>キーワードを入力して検索を実行してください。</p>
                    </div>
                </div>
            </div>
        `;
    },

    // Render individual company result
    renderCompanyResult(company) {
        return `
            <div class="result-item mb-4 p-3 border rounded bg-white">
                <div class="company-header">
                    <div class="d-flex justify-content-between align-items-start">
                        <div class="flex-grow-1">
                            <h5 class="company-title">
                                ${company.main_domain_url ?
                                    `<a href="${app.utils.escapeHtml(company.main_domain_url)}" target="_blank" class="company-link">${app.utils.escapeHtml(company.company_name_kj || company.company_name)}</a>` :
                                    app.utils.escapeHtml(company.company_name_kj || company.company_name)
                                }
                            </h5>
                            <div class="company-details">
                                ${company.jcn ? `<span class="badge badge-outline-primary me-2">法人番号: ${app.utils.escapeHtml(company.jcn)}</span>` : ''}<br>
                                ${company.LARGE_CLASS_NAME ? `<span class="badge badge-outline-primary me-2">${app.utils.escapeHtml(company.LARGE_CLASS_NAME)}</span>` : ''}
                                ${company.MIDDLE_CLASS_NAME ? `<span class="badge badge-outline-primary me-2">${app.utils.escapeHtml(company.MIDDLE_CLASS_NAME)}</span>` : ''}
                                ${company.city ? `<span class="badge badge-outline-primary me-2">${app.utils.escapeHtml(company.city)}</span>` : ''}
                                ${company.EMPLOYEE_ALL_NUM ? `<span class="badge badge-outline-primary me-2">従業員: ${app.utils.escapeHtml(company.EMPLOYEE_ALL_NUM)}人</span>` : ''}
                                ${company.CURR_SETLMNT_TAKING_AMT ? `<span class="badge badge-outline-primary me-2">売上: ${app.utils.escapeHtml(company.CURR_SETLMNT_TAKING_AMT)}</span>` : ''}
                            </div>
                        </div>
                        ${company.CUST_STATUS2 ? `
                        <div class="company-badges">
                            <span class="badge bg-secondary">${app.utils.escapeHtml(company.CUST_STATUS2)}</span>
                        </div>
                        ` : ''}
                    </div>
                </div>

                <div class="company-urls">
                    ${company.urls ? company.urls.map(url => `
                    <div class="url-item">
                        <div class="d-flex justify-content-between align-items-start">
                            <div class="flex-grow-1">
                                ${url.url ? `
                                <div class="url-title">
                                    <a href="${app.utils.escapeHtml(url.url)}" target="_blank">
                                        ${app.utils.escapeHtml(url.url_name)}
                                    </a>
                                </div>
                                ` : `
                                <div class="url-title">${app.utils.escapeHtml(url.url_name)}</div>
                                `}
                                ${url.content ? `
                                <div class="url-content">${app.utils.escapeHtml(url.content)}</div>
                                ` : ''}
                            </div>

                            ${url.matched_terms && url.matched_terms.length > 0 ? `
                            <div class="matched-terms-sidebar">
                                ${url.matched_terms.map(term =>
                                    `<span class="keyword-badge">${app.utils.escapeHtml(term)}</span>`
                                ).join('')}
                            </div>
                            ` : ''}
                        </div>
                    </div>
                    `).join('') : ''}
                </div>
            </div>
        `;
    },

    // Render history page
    async renderHistoryPage(params = {}) {
        try {
            const showAll = params.show_all === 'true';
            const response = await fetch(`/history${showAll ? '?show_all=true' : ''}`);

            if (!response.ok) {
                if (response.status === 401) {
                    return `
                        <div class="alert alert-warning">
                            <h5>ログインが必要です</h5>
                            <p>検索履歴を表示するにはログインが必要です。</p>
                            <button onclick="app.router.navigate('login')" class="btn btn-primary">
                                ログインページへ
                            </button>
                        </div>
                    `;
                }
                throw new Error(`History request failed with status: ${response.status}`);
            }

            const data = await response.json();

            return this.renderHistoryContent(data, showAll);

        } catch (error) {
            console.error('History error:', error);
            return `
                <div class="alert alert-danger">
                    <h5>履歴読み込みエラー</h5>
                    <p>履歴の読み込み中にエラーが発生しました。</p>
                    <p><small class="text-muted">エラー詳細: ${error.message}</small></p>
                    <button onclick="location.reload()" class="btn btn-outline-primary">
                        再読み込み
                    </button>
                </div>
            `;
        }
    },

    // Render history content
    renderHistoryContent(data, showAll) {
        const { searches, total_searches, username } = data;

        return `
            <div class="row">
                <div class="col-md-12">
                    ${searches && searches.length > 0 ? `
                    <div class="card">
                        <div class="card-header d-flex justify-content-between align-items-center">
                            <h5 class="mb-0">${app.utils.escapeHtml(username)}さんの検索履歴 (${total_searches}件)</h5>
                            <div class="btn-group btn-group-sm">
                                ${!showAll ? `
                                <a href="#" onclick="app.router.navigate('history', {show_all: 'true'})" class="btn btn-outline-primary">
                                    もっと見る (100件)
                                </a>
                                ` : `
                                <a href="#" onclick="app.router.navigate('history')" class="btn btn-outline-secondary">
                                    最新8件のみ
                                </a>
                                `}
                            </div>
                        </div>
                        <div class="card-body p-0">
                            <div class="table-responsive">
                                <table class="table table-hover mb-0">
                                    <thead class="table-light">
                                        <tr>
                                            <th>検索時刻</th>
                                            <th>検索クエリ</th>
                                            <th>検索条件</th>
                                            <th>結果数</th>
                                            <th>リスト作成</th>
                                            <th>アクション</th>
                                        </tr>
                                    </thead>
                                    <tbody>
                                        ${searches.map((search, index) => {
                                            const hasResults = (search.results_count || 0) > 0;

                                            return `
                                        <tr>
                                            <td>
                                                <small class="text-muted">
                                                    ${search.timestamp.split('T')[0]}<br>
                                                    ${search.timestamp.split('T')[1].split('.')[0]}
                                                </small>
                                            </td>
                                            <td>
                                                <strong>${app.utils.escapeHtml(search.query)}</strong>
                                            </td>
                                            <td>
                                                <div class="d-flex flex-wrap gap-1">
                                                    ${search.cust_status ? `<span class="badge bg-primary">${search.cust_status}</span>` : ''}
                                                    ${search.prefecture ? `<span class="badge bg-info">${search.prefecture}</span>` : ''}
                                                    ${search.city ? `<span class="badge bg-secondary">${search.city}</span>` : ''}
                                                </div>
                                            </td>
                                            <td>
                                                ${(search.results_count || 0) > 0 ?
                                                    `<span class="badge bg-success">${search.results_count || 0}件</span>` :
                                                    '<span class="badge bg-warning">0件</span>'
                                                }
                                            </td>
                                            <td>
                                                ${hasResults ?
                                                    `<button class="btn btn-sm btn-outline-success" onclick="alert('ダミー: リスト${index + 1}.csvをダウンロードしました')">
                                                        再発行
                                                    </button>` :
                                                    '<span class="text-muted">-</span>'
                                                }
                                            </td>
                                            <td>
                                                <a href="#" onclick="app.router.navigate('search', {q: '${app.utils.escapeHtml(search.query)}', prefecture: '${search.prefecture || ''}', city: '${search.city || ''}', cust_status: '${search.cust_status || ''}'})"
                                                   class="btn btn-sm btn-outline-primary">再検索</a>
                                            </td>
                                        </tr>
                                        `;
                                        }).join('')}
                                    </tbody>
                                </table>
                            </div>
                        </div>
                    </div>
                    ` : `
                    <div class="alert alert-info">
                        <h5>検索履歴がありません</h5>
                        <p>まだ検索を行っていません。<a href="#" onclick="app.router.navigate('home')">検索ページ</a>で検索を開始してください。</p>
                    </div>
                    `}
                </div>
            </div>
        `;
    },

    // Render rankings page
    async renderRankingsPage() {
        try {
            // Fetch both rankings data and user rankings in parallel
            const [rankingsResponse, userRankingsResponse] = await Promise.all([
                fetch('/rankings'),
                fetch('/api/user-rankings?limit=10')
            ]);

            if (!rankingsResponse.ok) {
                if (rankingsResponse.status === 401) {
                    return `
                        <div class="alert alert-warning">
                            <h5>ログインが必要です</h5>
                            <p>ランキングを表示するにはログインが必要です。</p>
                            <button onclick="app.router.navigate('login')" class="btn btn-primary">
                                ログインページへ
                            </button>
                        </div>
                    `;
                }
                throw new Error(`Rankings request failed with status: ${rankingsResponse.status}`);
            }

            const data = await rankingsResponse.json();
            const userRankings = userRankingsResponse.ok ? await userRankingsResponse.json() : [];

            return this.renderRankingsContent(data, userRankings);

        } catch (error) {
            console.error('Rankings error:', error);
            return `
                <div class="alert alert-danger">
                    <h5>ランキング読み込みエラー</h5>
                    <p>ランキングの読み込み中にエラーが発生しました。</p>
                    <p><small class="text-muted">エラー詳細: ${error.message}</small></p>
                    <button onclick="location.reload()" class="btn btn-outline-primary">
                        再読み込み
                    </button>
                </div>
            `;
        }
    },

    // Render rankings content
    renderRankingsContent(data, userRankings = []) {
        const { keywords, queries, stats, username } = data;

        return `
            <div class="row">
                <div class="col-md-12">
                    ${keywords && keywords.length > 0 || queries && queries.length > 0 ? `
                    <!-- Dual Rankings Tables -->
                    <div class="row">
                        <!-- Keywords Ranking (Left) -->
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h5 class="mb-0">人気キーワード TOP ${keywords?.length || 0}</h5>
                                    <p class="text-muted mb-0">単一のキーワードで集計</p>
                                </div>
                                <div class="card-body p-0">
                                    ${keywords && keywords.length > 0 ? `
                                    <div class="table-responsive">
                                        <table class="table table-hover mb-0">
                                            <thead class="table-light">
                                                <tr>
                                                    <th style="width: 60px;">順位</th>
                                                    <th>キーワード</th>
                                                    <th style="width: 80px;">回数</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                ${keywords.map((keyword, index) => `
                                                <tr>
                                                    <td>
                                                        ${index < 3 ?
                                                            (index === 0 ? '<span class="badge bg-warning text-dark">🥇</span>' :
                                                             index === 1 ? '<span class="badge bg-secondary">🥈</span>' :
                                                             '<span class="badge bg-dark text-white">🥉</span>') :
                                                            `<span class="badge bg-primary">${index + 1}</span>`
                                                        }
                                                    </td>
                                                    <td>
                                                        <span class="fw-bold">${app.utils.escapeHtml(keyword.keyword)}</span>
                                                    </td>
                                                    <td>
                                                        <span class="badge bg-success">${keyword.count}</span>
                                                    </td>
                                                </tr>
                                                `).join('')}
                                            </tbody>
                                        </table>
                                    </div>
                                    ` : `
                                    <div class="text-center py-4">
                                        <p class="text-muted">キーワードデータなし</p>
                                    </div>
                                    `}
                                </div>
                            </div>
                        </div>

                        <!-- Queries Ranking (Right) -->
                        <div class="col-md-6">
                            <div class="card">
                                <div class="card-header">
                                    <h5 class="mb-0">人気検索クエリ TOP ${queries?.length || 0}</h5>
                                    <p class="text-muted mb-0">検索クエリで集計</p>
                                </div>
                                <div class="card-body p-0">
                                    ${queries && queries.length > 0 ? `
                                    <div class="table-responsive">
                                        <table class="table table-hover mb-0">
                                            <thead class="table-light">
                                                <tr>
                                                    <th style="width: 60px;">順位</th>
                                                    <th>検索クエリ</th>
                                                    <th style="width: 80px;">回数</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                ${queries.map((query, index) => `
                                                <tr>
                                                    <td>
                                                        ${index < 3 ?
                                                            (index === 0 ? '<span class="badge bg-warning text-dark">🥇</span>' :
                                                             index === 1 ? '<span class="badge bg-secondary">🥈</span>' :
                                                             '<span class="badge bg-dark text-white">🥉</span>') :
                                                            `<span class="badge bg-primary">${index + 1}</span>`
                                                        }
                                                    </td>
                                                    <td>
                                                        <span class="fw-bold">${app.utils.escapeHtml(query.query)}</span>
                                                    </td>
                                                    <td>
                                                        <span class="badge bg-info">${query.count}</span>
                                                    </td>
                                                </tr>
                                                `).join('')}
                                            </tbody>
                                        </table>
                                    </div>
                                    ` : `
                                    <div class="text-center py-4">
                                        <p class="text-muted">検索クエリデータなし</p>
                                    </div>
                                    `}
                                </div>
                            </div>
                        </div>
                    </div>

                    <!-- User Rankings Section -->
                    <div class="row mt-4">
                        <div class="col-md-12">
                            <div class="card">
                                <div class="card-header">
                                    <h5 class="mb-0">👥 ユーザー利用ランキング TOP ${userRankings?.length || 0}</h5>
                                    <p class="text-muted mb-0">検索回数によるユーザーランキング</p>
                                </div>
                                <div class="card-body p-0">
                                    ${userRankings && userRankings.length > 0 ? `
                                    <div class="table-responsive">
                                        <table class="table table-hover mb-0">
                                            <thead class="table-light">
                                                <tr>
                                                    <th style="width: 60px;">順位</th>
                                                    <th>ユーザー名</th>
                                                    <th style="width: 100px;">検索回数</th>
                                                    <th style="width: 150px;">アクティブ度</th>
                                                </tr>
                                            </thead>
                                            <tbody>
                                                ${userRankings.map((user, index) => `
                                                <tr ${user.username === username ? 'class="table-warning"' : ''}>
                                                    <td>
                                                        ${index < 3 ?
                                                            (index === 0 ? '<span class="badge bg-warning text-dark">🥇</span>' :
                                                             index === 1 ? '<span class="badge bg-secondary">🥈</span>' :
                                                             '<span class="badge bg-dark text-white">🥉</span>') :
                                                            `<span class="badge bg-primary">${index + 1}</span>`
                                                        }
                                                    </td>
                                                    <td>
                                                        <div class="d-flex align-items-center">
                                                            <span class="fw-bold ${user.username === username ? 'text-warning' : ''}">${app.utils.escapeHtml(user.username)}</span>
                                                            ${user.username === username ? '<span class="badge bg-warning text-dark ms-2">あなた</span>' : ''}
                                                        </div>
                                                    </td>
                                                    <td>
                                                        <span class="badge ${user.search_count > 200 ? 'bg-success' : user.search_count > 100 ? 'bg-info' : 'bg-secondary'}">${user.search_count}</span>
                                                    </td>
                                                    <td>
                                                        ${user.search_count > 200 ?
                                                            '<span class="text-success">🔥 高</span>' :
                                                            user.search_count > 100 ?
                                                            '<span class="text-info">📈 中</span>' :
                                                            '<span class="text-muted">📊 低</span>'
                                                        }
                                                    </td>
                                                </tr>
                                                `).join('')}
                                            </tbody>
                                        </table>
                                    </div>
                                    ` : `
                                    <div class="text-center py-4">
                                        <p class="text-muted">ユーザーデータなし</p>
                                    </div>
                                    `}
                                </div>
                            </div>
                        </div>
                    </div>

                    ` : `
                    <!-- Empty State -->
                    <div class="text-center py-5">
                        <div class="mb-4">
                            <i style="font-size: 4rem;">📊</i>
                        </div>
                        <h4 class="mb-3">検索データを収集中...</h4>
                        <p class="text-muted mb-4">
                            まだ十分な検索データがありません。<br>
                            検索を使い始めると、人気のキーワードランキングがここに表示されます。
                        </p>
                        <a href="#" onclick="app.router.navigate('home')" class="btn btn-primary">
                            <i class="me-1">🔍</i> 検索を始める
                        </a>
                    </div>
                    `}

                    <!-- Navigation Links -->
                    <div class="mt-5">
                        <hr>
                        <div class="d-flex justify-content-between align-items-center">
                            <small class="text-muted">
                                リアルタイム更新 | ${app.utils.escapeHtml(username)}さん
                            </small>
                        </div>
                    </div>
                </div>
            </div>
        `;
    }
};