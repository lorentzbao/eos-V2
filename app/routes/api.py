from flask import Blueprint, request, jsonify, Response, session
from app.services.search_service import SearchService
import csv
import io
from datetime import datetime
import urllib.parse

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

@api.route('/download-csv')
def download_csv():
    """Download search results as CSV with cursor-based streaming"""
    # Check authentication
    if 'username' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get search parameters
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'auto')
    prefecture = request.args.get('prefecture', '')
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    def escape_csv_field(field):
        """Properly escape CSV fields with quotes and commas"""
        if field is None:
            return ""
        
        field_str = str(field)
        
        # If field contains quotes, commas, or newlines, wrap in quotes and escape internal quotes
        if '"' in field_str or ',' in field_str or '\n' in field_str or '\r' in field_str:
            # Escape quotes by doubling them
            field_str = field_str.replace('"', '""')
            return f'"{field_str}"'
        
        return field_str
    
    def generate_csv_stream():
        """Generate CSV data stream efficiently with proper UTF-8 handling"""
        try:
            # Use Python's CSV writer for proper encoding
            output = io.StringIO()
            
            # UTF-8 BOM for Excel compatibility
            yield '\ufeff'
            
            # Create CSV writer
            fieldnames = ['ID', 'Title', 'Content', 'URL', 'Score', 'Prefecture', 'Matched_Terms']
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            yield output.getvalue()
            output.seek(0)
            output.truncate(0)
            
            # Single search to get all results - most efficient approach
            search_results = search_service.search(query, limit=10000, search_type=search_type, prefecture=prefecture)
            results = search_results.get('results', [])
            
            batch = []
            batch_size = 100  # Process in batches to manage memory
            record_count = 0
            
            for result in results:
                # Format result data
                result_data = {
                    'ID': result.get('id', ''),
                    'Title': result.get('title', ''),
                    'Content': result.get('content', '')[:500],  # Limit content length
                    'URL': result.get('url', ''),
                    'Score': round(result.get('score', 0), 3),
                    'Prefecture': prefecture if prefecture else 'all',
                    'Matched_Terms': '|'.join(result.get('matched_terms', []))
                }
                
                batch.append(result_data)
                record_count += 1
                
                # Process batch when full
                if len(batch) >= batch_size:
                    for item in batch:
                        writer.writerow(item)
                    
                    yield output.getvalue()
                    output.seek(0)
                    output.truncate(0)
                    batch = []  # Clear memory
                    
            # Process remaining items in final batch
            for item in batch:
                writer.writerow(item)
                
            if batch:  # If there were remaining items
                yield output.getvalue()
                output.seek(0)
                output.truncate(0)
                
            # No summary needed per user request
            
        except Exception as e:
            error_msg = f"\n# Error occurred during export: {str(e)}\n"
            yield error_msg
    
    # Generate simple filename with timestamp
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"search_results_{timestamp}.csv"
    
    # Set response headers for download with proper encoding
    headers = {
        'Content-Disposition': f'attachment; filename="{filename}"',
        'Content-Type': 'text/csv; charset=utf-8'
    }
    
    return Response(
        generate_csv_stream(), 
        headers=headers,
        mimetype='text/csv'
    )

