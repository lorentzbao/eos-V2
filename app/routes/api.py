from flask import Blueprint, request, jsonify
from app.services.search_service import SearchService

api = Blueprint('api', __name__, url_prefix='/api')
search_service = SearchService()

@api.route('/search')
def api_search():
    """API endpoint for search queries"""
    query = request.args.get('q', '')
    search_type = request.args.get('type', 'auto')
    limit = int(request.args.get('limit', 10))
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    results = search_service.search(query, limit, search_type)
    return jsonify(results)

@api.route('/add_document', methods=['POST'])
def api_add_document():
    """API endpoint to add a single document"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['id', 'title', 'content']):
        return jsonify({'error': 'Missing required fields: id, title, content'}), 400
    
    try:
        success = search_service.add_document(
            data['id'], 
            data['title'], 
            data['content'], 
            data.get('url', '')
        )
        if success:
            return jsonify({'success': True, 'message': 'Document added successfully'})
        else:
            return jsonify({'error': 'Failed to add document'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/add_documents', methods=['POST'])
def api_add_documents():
    """API endpoint to add multiple documents in batch"""
    data = request.get_json()
    
    if not data or 'documents' not in data:
        return jsonify({'error': 'Missing documents field'}), 400
    
    documents = data['documents']
    if not isinstance(documents, list):
        return jsonify({'error': 'Documents must be an array'}), 400
    
    # Validate each document
    for i, doc in enumerate(documents):
        if not all(k in doc for k in ['id', 'title', 'content']):
            return jsonify({'error': f'Document {i}: Missing required fields: id, title, content'}), 400
    
    try:
        success = search_service.add_documents_batch(documents)
        if success:
            return jsonify({
                'success': True, 
                'message': f'{len(documents)} documents added successfully'
            })
        else:
            return jsonify({'error': 'Failed to add documents'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/stats')
def api_stats():
    """API endpoint to get search engine statistics"""
    return jsonify(search_service.get_stats())

@api.route('/clear_index', methods=['POST'])
def api_clear_index():
    """API endpoint to clear the search index"""
    try:
        success = search_service.clear_index()
        if success:
            return jsonify({'success': True, 'message': 'Index cleared successfully'})
        else:
            return jsonify({'error': 'Failed to clear index'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@api.route('/optimize_index', methods=['POST'])
def api_optimize_index():
    """API endpoint to optimize the search index"""
    try:
        success = search_service.optimize_index()
        if success:
            return jsonify({'success': True, 'message': 'Index optimized successfully'})
        else:
            return jsonify({'error': 'Failed to optimize index'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

