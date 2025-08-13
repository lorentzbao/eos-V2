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
    page = int(request.args.get('page', 1))
    per_page = 20
    
    # Get user's search history
    all_searches = search_logger.get_user_searches(username, limit=1000)
    
    # Pagination
    start = (page - 1) * per_page
    end = start + per_page
    searches = all_searches[start:end]
    
    # Calculate pagination info
    total_searches = len(all_searches)
    total_pages = (total_searches + per_page - 1) // per_page
    has_prev = page > 1
    has_next = page < total_pages
    
    return render_template('history.html',
                         username=username,
                         searches=searches,
                         page=page,
                         total_pages=total_pages,
                         total_searches=total_searches,
                         has_prev=has_prev,
                         has_next=has_next)

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