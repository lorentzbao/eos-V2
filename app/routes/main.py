from flask import Blueprint, render_template, request, jsonify
from app.services.search_service import SearchService

main = Blueprint('main', __name__)
search_service = SearchService()

@main.route('/')
def index():
    return render_template('index.html')

@main.route('/search')
def search():
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

@main.route('/api/search')
def api_search():
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'auto')
    limit = int(request.args.get('limit', 10))
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    results = search_service.search(query, limit, search_type)
    return jsonify(results)

@main.route('/api/add_document', methods=['POST'])
def api_add_document():
    data = request.get_json()
    
    if not data or not all(k in data for k in ['id', 'title', 'content']):
        return jsonify({'error': 'Missing required fields: id, title, content'}), 400
    
    try:
        search_service.add_document(
            data['id'], 
            data['title'], 
            data['content'], 
            data.get('url', '')
        )
        return jsonify({'success': True, 'message': 'Document added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@main.route('/api/stats')
def api_stats():
    return jsonify(search_service.get_stats())