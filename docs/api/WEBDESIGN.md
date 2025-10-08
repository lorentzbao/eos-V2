## 1. プロジェクト概要
### 1.1 プロジェクト名
Enterprise Online Search(EOS)

## 2. デザイン要件
### 2.1 Brand Color
- **Primary**
  - rgb(0, 24, 113) #001871
  - rgb(19, 82, 222) #1352DE
  - rgb(199, 219, 244) #C7DBF4
- **Accnet**
  - rgb(255, 191, 63) #FFBF3F
  - rgb(246, 140, 162) #F68CA2
  - rgb(0, 164, 228) #00A4E4
- **Background**
  - rgb(255, 255, 255) #FFFFFF
  - rgb(208, 208, 208) #D0D0D0
- **Basic Font**
  - rgb(255, 255, 255) #FFFFFF
  - rgb(0, 0, 0) #000000

### 2.2 画面構成
- **ログイン画面**
  - ユーザー登録 : Microsoft Formsのサイトに移動（"https://forms.office.com/pages/responsepage.aspx?id=test"）
  - ログインはLANIDだけ入力（パスワードはなし）
- **基本画面構成**
  - Side Bar
    - Item : EOSとは、キーワード検索、ランキング、検索履歴、
    - Background Color : #001871
  - Header
    - 左側に「Enterprise Online Search(EOS)」というタイトルを入れる
    - タイトルクリック時: キーワード検索ページに遷移
    - Item :（右側寄せ）「所属　ユーザー名」、通知、ヘルプ、ログアウト
    - Background Color : #FFFFFF
  - Body
    - Background Color : #D0D0D0
    - Basic Button Color : #001871
- **EOSとは**
  - Sharepoint Listに移動("https://share.connect.test/sites/eos")
  - 新しいタブを開くようにする
- **キーワード検索**
  - 対象選択（必須）
    - ラジオボタンをボタン風デザインで実装
    - 対象: 白地・過去 or 契約
    - Background: var(--primary-dark), Border: 2px solid
    - 選択時: gradient background with animation
  - 条件設定（条件分岐）
    - 白地・過去を選んだ場合: 都道府県（必須）、市区町村（任意）
    - 契約を選んだ場合: 地域事業本部（必須）、支店（任意）、ソリシター（任意）
  - キーワード検索バー
    - search-containerの幅をapp-container幅に拡張
    - 検索候補: クリック時のみ表示（フォーカス時は非表示）
    - ユーザー全体の検索履歴からの人気キーワードを表示
  - 表示オプション
    - 検索実行後に検索フォーム直下に表示
    - 結果表示件数: デフォルト100件（ユーザー選択不可）
    - マッチ方式: すべてのキーワード/一部のキーワード選択可能
    - 高さを低く調整したコンパクトデザイン
  - 検索結果
    - 企業単位でグルーピング表示（カード形式）
    - 企業情報: 企業名（main_domain_urlがあればリンク化）、法人番号、業種、住所、従業員数、売上高
    - 企業詳細情報: badge-outline-primary デザイン（背景透明、primary-blue枠線）
    - 関連ページ: ページタイトル（ハイパーリンク）、マッチキーワード
    - キーワードデザイン: 角が丸い四角形、Color - #FFBF3F, Font Color - #001871
  - リスト作成
    - ダウンロードボタン: btn-primary-dark（primary-dark背景、白文字）
    - 検索結果があるときのみ表示
  - 検索ヒント
    - 対象選択、条件絞り込み、表示オプションの説明
    - 白地・過去と契約の条件要件説明
    - 現在の仕様に合わせた内容に更新
- **ランキング**
  - 3つのランキングを表示
    - 人気キーワードランキング: 単一キーワードで集計
    - 人気検索クエリランキング: 検索クエリで集計
    - ユーザー利用ランキング: 検索回数によるユーザーランキング（ダミーデータ）
  - ページタイトル: 🏆 キーワード・ランキング
  - 統計情報表示は削除
  - 各ランキングは左右2列 + 下部1列の配置
  - ユーザーランキング: 現在ユーザーをハイライト表示、アクティブ度表示
- **検索履歴**
  - テーブル構成変更
    - 検索時刻、検索クエリ、検索条件、結果数、リスト作成、アクション
    - 検索時間列を削除
  - 検索条件表示
    - 対象（白地・過去/契約）をプライマリバッジで表示
    - 都道府県、市区町村、地域事業本部、支店、ソリシターを色分けバッジで表示
  - リスト作成機能
    - 結果がある検索にCSVダウンロードボタン表示（ダミー実装）
  - 再検索機能: 新しい検索条件パラメータに対応

## 3. Front-End ファイル構造

### 3.1 HTMLテンプレート
- `templates/app.html` - メインアプリケーションテンプレート
  - Bootstrap 5.1.3を使用
  - レスポンシブデザイン対応
  - ログインレイアウトとメインレイアウトの切り替え
  - 動的コンテンツ読み込み用のコンテナ

### 3.2 CSS スタイルシート（依存関係順）
- `static/css/styles_basic.css` - 基本スタイル・CSS変数定義
  - EOSブランドカラーの CSS Custom Properties
  - 基本的なボタンスタイル
  - ユーティリティクラス
- `static/css/styles_main.css` - メインレイアウトスタイル
  - ヘッダー、サイドバー、メインコンテンツエリア
  - ナビゲーション、ユーザー情報表示
- `static/css/styles_login.css` - ログインページ専用スタイル
  - ログインフォーム、レイアウト
  - ユーザー登録ボタン
- `static/css/styles_search.css` - 検索機能専用スタイル
  - 検索フォーム、結果表示
  - ラジオボタンのボタン風デザイン
  - 検索候補ドロップダウン
  - 企業情報カード、バッジスタイル
  - 表示オプション、ダウンロードボタン

### 3.3 JavaScript モジュール（読み込み順）
- `static/js/app.js` - メインアプリケーション管理
  - アプリケーション状態管理
  - 初期化処理
  - ユーティリティ関数
  - フォーム処理機能
- `static/js/auth.js` - 認証機能
  - ログイン・ログアウト処理
  - ユーザー状態管理
- `static/js/router.js` - ページルーティング
  - SPA ナビゲーション
  - ページ初期化
  - URL履歴管理
- `static/js/pages.js` - ページレンダリング
  - 各ページのHTML生成
  - ダイナミックコンテンツ
  - 検索結果表示
  - ダミーデータ管理
- `static/js/search.js` - 検索機能
  - 検索候補表示
  - キーボードナビゲーション
  - 検索API呼び出し
- `static/js/pagination.js` - ページネーション機能
  - 検索結果のページ分割
- `static/js/csv-download.js` - CSV ダウンロード機能
  - リスト作成・ダウンロード処理

### 3.4 主要機能とファイルの対応

#### ログイン機能
- **Templates**: `app.html` (loginLayout)
- **CSS**: `styles_login.css`
- **JS**: `auth.js`, `pages.js` (renderLoginPage)

#### キーワード検索機能
- **Templates**: `app.html` (mainLayout)
- **CSS**: `styles_search.css`
- **JS**: `pages.js` (renderHomePage, renderSearchPage), `search.js`, `router.js`

#### ランキング機能
- **Templates**: `app.html` (mainLayout)
- **CSS**: `styles_main.css`, `styles_search.css`
- **JS**: `pages.js` (renderRankingsPage), `router.js`

#### 検索履歴機能
- **Templates**: `app.html` (mainLayout)
- **CSS**: `styles_main.css`
- **JS**: `pages.js` (renderHistoryPage), `router.js`

### 3.5 ダミーデータ実装箇所
- `pages.js` の `renderRankingsContent()` - ユーザーランキングダミーデータ
- `pages.js` の `renderHistoryContent()` - 検索条件ダミーデータ
- CSV ダウンロード機能 - アラート表示によるダミー実装

## 4. Back-End修正要件

### 4.1 検索機能の拡張
#### 検索条件パラメータの追加
- 既存の `q` (検索クエリ) に加えて以下のパラメータを受け取る
  - `target`: 白地・過去 / 契約
  - `prefecture`: 都道府県（白地・過去選択時）
  - `city`: 市区町村（白地・過去選択時、任意）
  - `regional_office`: 地域事業本部（契約選択時）
  - `branch`: 支店（契約選択時、任意）
  - `solicitor`: ソリシター（契約選択時、任意）
  - `search_option`: マッチ方式（all/exact/partial）
  - `limit`: 結果表示件数（デフォルト100）

#### 検索結果データ構造の拡張
- 企業情報に `main_domain_url` フィールドを追加
  - 企業名をクリック可能なリンクとして表示するため
- 検索履歴に以下の条件情報を保存
  - 選択された対象（白地・過去/契約）
  - 各種絞り込み条件（都道府県、地域事業本部等）

### 4.2 ランキング機能の拡張
#### 新規APIエンドポイント: `/api/user-rankings`
- ユーザーの検索回数に基づくランキングを返す
- レスポンス例:
```json
{
  "user_rankings": [
    {
      "username": "田中太郎",
      "search_count": 245,
      "rank": 1
    }
  ]
}
```

#### 既存 `/rankings` エンドポイントの修正
- ページタイトル用データ追加
- 統計情報セクションの削除（フロントエンドに合わせて）

### 4.3 検索履歴機能の拡張
#### `/history` エンドポイントのレスポンス拡張
- 各検索履歴項目に検索条件の詳細を追加
```json
{
  "searches": [
    {
      "query": "検索キーワード",
      "timestamp": "2024-01-01T10:00:00",
      "results_count": 50,
      "target": "白地・過去",
      "prefecture": "tokyo",
      "city": "shibuya",
      "regional_office": null,
      "branch": null,
      "solicitor": null,
      "search_option": "all",
      "csv_file_id": "unique_file_id" // リスト作成用
    }
  ]
}
```

### 4.4 CSV/リスト作成機能
#### 新規API エンドポイント: `/api/create-list`
- 検索結果からCSVファイルを生成
- パラメータ: 検索条件（上記の全パラメータ）
- レスポンス: ファイルID または ダウンロードURL

#### 新規API エンドポイント: `/api/download-list/<file_id>`
- 生成されたCSVファイルをダウンロード
- 検索履歴の各項目と紐付け

### 4.5 データベース スキーマ修正
#### 検索履歴テーブル (`search_history`)
- 既存フィールドに追加:
  - `target` VARCHAR(20) - 対象選択
  - `prefecture` VARCHAR(50) - 都道府県
  - `city` VARCHAR(50) - 市区町村
  - `regional_office` VARCHAR(50) - 地域事業本部
  - `branch` VARCHAR(50) - 支店
  - `solicitor` VARCHAR(50) - ソリシター
  - `search_option` VARCHAR(20) - マッチ方式
  - `csv_file_id` VARCHAR(100) - 生成されたCSVファイルID

#### 企業情報テーブル
- `main_domain_url` フィールドの追加または既存フィールドの活用

#### 新規テーブル: `generated_files`
- `file_id` VARCHAR(100) PRIMARY KEY
- `user_id` VARCHAR(50) - 生成ユーザー
- `search_conditions` TEXT - 検索条件のJSON
- `file_path` VARCHAR(255) - ファイル保存パス
- `created_at` TIMESTAMP
- `expires_at` TIMESTAMP - ファイル有効期限

### 4.6 バリデーション強化
#### 検索条件の必須チェック
- `target` が "白地・過去" の場合、`prefecture` が必須
- `target` が "契約" の場合、`regional_office` が必須
- 無効な組み合わせの場合はエラーレスポンス

### 4.7 パフォーマンス最適化
#### 検索クエリの最適化
- 新しい検索条件に対応したインデックス追加
- 複合検索条件での効率的なクエリ実行

#### ファイル管理
- 生成されたCSVファイルの定期クリーンアップ
- ファイル有効期限の自動管理
