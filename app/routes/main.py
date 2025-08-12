from flask import Blueprint, render_template, request
from app.services.search_service import SearchService

main = Blueprint('main', __name__)
search_service = SearchService()

@main.route('/')
def index():
    """Main search page"""
    return render_template('index.html')

@main.route('/search')
def search():
    """Search results page"""
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'auto')
    limit = int(request.args.get('limit', 10))
    
    if not query:
        return render_template('search.html', 
                             query='', 
                             results=[], 
                             stats={'total_documents': search_service.get_stats()['total_documents']})
    
    search_results = search_service.search(query, limit, search_type)
    stats = search_service.get_stats()
    
    return render_template('search.html', 
                         query=query,
                         results=search_results['results'],
                         total_found=search_results['total_found'],
                         search_time=search_results['search_time'],
                         processed_query=search_results['processed_query'],
                         stats=stats)