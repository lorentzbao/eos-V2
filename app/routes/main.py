from flask import Blueprint, render_template, request, session, redirect, url_for
from app.services.search_service import SearchService
from app.services.search_logger import SearchLogger

main = Blueprint('main', __name__)
search_service = SearchService()
search_logger = SearchLogger()

@main.route('/')
def index():
    """Main search page"""
    if 'username' not in session:
        return redirect(url_for('main.login'))
    return render_template('index.html', username=session['username'])

@main.route('/login', methods=['GET', 'POST'])
def login():
    """Login page"""
    if request.method == 'POST':
        username = request.form.get('username', '').strip()
        if username:
            session['username'] = username
            return redirect(url_for('main.index'))
        else:
            return render_template('login.html', error='ユーザー名を入力してください', username=username)
    
    return render_template('login.html')

@main.route('/logout')
def logout():
    """Logout and clear session"""
    session.pop('username', None)
    return redirect(url_for('main.login'))

@main.route('/history')
def history():
    """Search history page"""
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    username = session['username']
    
    # Get limit from query parameter, default to 10
    limit = int(request.args.get('limit', 10))
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
    
    return render_template('history.html',
                         username=username,
                         searches=searches,
                         total_searches=total_searches,
                         limit=limit,
                         show_all=show_all)

@main.route('/search')
def search():
    """Search results page"""
    if 'username' not in session:
        return redirect(url_for('main.login'))
    
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'auto')
    limit = int(request.args.get('limit', 10))
    username = session['username']
    
    if not query:
        return render_template('search.html', 
                             query='', 
                             results=[], 
                             username=username,
                             stats={'total_documents': search_service.get_stats()['total_documents']})
    
    search_results = search_service.search(query, limit, search_type)
    stats = search_service.get_stats()
    
    # Log the search query with detailed information
    search_logger.log_search(
        username, 
        query, 
        search_type, 
        search_results['total_found'], 
        search_results['search_time']
    )
    
    return render_template('search.html', 
                         query=query,
                         results=search_results['results'],
                         total_found=search_results['total_found'],
                         search_time=search_results['search_time'],
                         processed_query=search_results['processed_query'],
                         username=username,
                         stats=stats)