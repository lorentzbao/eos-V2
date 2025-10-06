from flask import Blueprint, render_template, request, session, redirect, url_for, current_app, jsonify
from app.services.search_service import SearchService
from app.services.multi_index_search_service import MultiIndexSearchService
from app.services.search_logger import SearchLogger

main = Blueprint('main', __name__)
search_logger = SearchLogger()

def get_search_service():
    """Get appropriate search service (multi-index or single-index)"""
    # Check if multi-index configuration is available
    if 'INDEXES' in current_app.config:
        return MultiIndexSearchService(current_app.config['INDEXES'])
    else:
        # Fallback to single index
        index_dir = current_app.config.get('INDEX_DIR', 'data/whoosh_index')
        return SearchService(index_dir)

@main.route('/')
def index():
    """Main application page - serves the SPA"""
    # If user is not logged in, serve app.html for login page
    if 'username' not in session:
        return render_template('app.html')

    # If user is logged in, serve app.html with user context
    # Get popular queries for search suggestions
    popular_queries = search_logger.get_popular_queries(limit=10)

    return render_template('app.html',
                         username=session.get('username'),
                         popular_queries=popular_queries)

@main.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if username:
            session['username'] = username
            return redirect(url_for('main.index'))
        else:
            return render_template('app.html', error='ユーザー名を入力してください', username=username)

    # If already logged in, redirect to main page
    if 'username' in session:
        return redirect(url_for('main.index'))

    return render_template('app.html')

@main.route('/logout', methods=['POST'])
def logout():
    """Logout and clear session"""
    session.pop('username', None)
    return redirect(url_for('main.index'))

@main.route('/rankings')
def rankings():
    """Search rankings API endpoint"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    username = session['username']

    # Get popular queries, keywords and stats
    popular_queries = search_logger.get_popular_queries(limit=10)
    popular_keywords = search_logger.get_popular_keywords(limit=10)
    ranking_stats = search_logger.get_rankings_stats()

    return jsonify({
        'username': username,
        'queries': popular_queries,
        'keywords': popular_keywords,
        'stats': ranking_stats
    })

@main.route('/history')
def history():
    """Search history API endpoint"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    username = session['username']

    # Get limit from query parameter, default to 8
    limit = int(request.args.get('limit', 8))
    show_all = request.args.get('show_all', 'false').lower() == 'true'

    # If show_all is requested, get more entries
    if show_all:
        limit = 100  # Still cap at reasonable number for performance

    # Get user's search history (optimized for latest entries)
    searches = search_logger.get_user_searches(username, limit=limit)

    # Get total count for statistics (this might be expensive for very large files)
    total_searches = len(searches)
    if show_all:
        # For show_all, we might have hit the cap, so this is approximate
        total_searches = f"{total_searches}+" if len(searches) == limit else str(total_searches)

    return jsonify({
        'username': username,
        'searches': searches,
        'total_searches': total_searches,
        'limit': limit,
        'show_all': show_all
    })

@main.route('/search')
def search():
    """Search results API endpoint"""
    if 'username' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 10))
    prefecture = request.args.get('prefecture', '')
    city = request.args.get('city', '')
    target = request.args.get('target', '')
    cust_status = request.args.get('cust_status', '')  # Keep for backward compatibility
    username = session['username']

    # Map target selection to CUST_STATUS2 filter
    # "白地・過去" means search for CUST_STATUS2 = "白地" OR "過去"
    # "契約" means search for CUST_STATUS2 = "契約"
    cust_status_filter = cust_status  # Use existing if provided
    if target == '白地・過去':
        cust_status_filter = '白地|過去'  # Use pipe to indicate OR logic
    elif target == '契約':
        cust_status_filter = '契約'

    # Handle empty or whitespace-only queries
    if not query or not query.strip():
        return jsonify({'error': 'Query is required'}), 400

    search_service = get_search_service()

    # Handle multi-index service
    if isinstance(search_service, MultiIndexSearchService):
        if not prefecture:
            return jsonify({'error': 'Prefecture is required'}), 400
        search_results = search_service.search(query, prefecture, limit, cust_status_filter, "", city)
        stats = search_service.get_stats(prefecture)
    else:
        # Single index service (backward compatibility)
        search_results = search_service.search(query, limit, prefecture, cust_status_filter, "", city)
        stats = search_service.get_stats()

    # Log the search query with detailed information
    search_logger.log_search(
        username,
        query,
        search_results['total_found'],
        search_results['search_time'],
        prefecture,
        cust_status
    )

    return jsonify({
        'query': query,
        'grouped_results': search_results.get('grouped_results', []),
        'total_found': search_results['total_found'],
        'total_companies': search_results.get('total_companies', 0),
        'search_time': search_results['search_time'],
        'processed_query': search_results['processed_query'],
        'prefecture': prefecture,
        'city': city,
        'cust_status': cust_status,
        'limit': limit,
        'username': username,
        'stats': stats
    })

@main.route('/api/popular-queries')
def api_popular_queries():
    """Popular queries API endpoint"""
    popular_queries = search_logger.get_popular_queries(limit=10)
    return jsonify(popular_queries)