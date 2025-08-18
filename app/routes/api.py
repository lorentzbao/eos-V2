from flask import Blueprint, request, jsonify, session, send_file
from app.services.search_service import SearchService
import csv
import io
import os
import hashlib
from datetime import datetime

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
            data.get('content', ''),  # Use content as introduction since no separate field
            data.get('url', ''),
            data.get('prefecture', '')
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

def get_cache_key(query, search_type, prefecture):
    """Generate unique cache key for search parameters"""
    params = f"{query}:{search_type}:{prefecture}"
    return hashlib.md5(params.encode('utf-8')).hexdigest()

@api.route('/download-csv')
def download_csv():
    """Download search results as CSV with file-based caching"""
    # Check authentication
    if 'username' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get search parameters
    query = request.args.get('q', '').strip()
    search_type = request.args.get('type', 'auto')
    prefecture = request.args.get('prefecture', '')
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    # Generate cache key and file path
    cache_key = get_cache_key(query, search_type, prefecture)
    # Use absolute path from project root
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))
    cache_dir = os.path.join(project_root, "data", "csv_cache")
    cache_file = os.path.join(cache_dir, f"{cache_key}.csv")
    
    # Check if cached file exists
    if os.path.exists(cache_file):
        # Generate filename for download
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        filename = f"search_results_{timestamp}.csv"
        
        # Serve cached file immediately
        return send_file(cache_file, as_attachment=True, download_name=filename)
    
    # File doesn't exist, generate and cache it
    def generate_csv_content():
        """Generate CSV content and save to cache file"""
        try:
            # Create cache directory if it doesn't exist
            os.makedirs(cache_dir, exist_ok=True)
            
            # Use Python's CSV writer for proper encoding
            output = io.StringIO()
            
            # Create CSV writer with company-focused field order
            fieldnames = ['Company_Number', 'Company_Name', 'Company_Tel', 'Company_Industry', 'Prefecture', 'URL_Name', 'URL', 'Content', 'Matched_Terms', 'ID']
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Single search to get all results - most efficient approach with company_number sorting
            search_results = search_service.search(query, limit=10000, search_type=search_type, prefecture=prefecture, sort_by="company_number")
            grouped_results = search_results.get('grouped_results', [])
            
            # Write all results by flattening grouped results
            for company in grouped_results:
                for url in company.get('urls', []):
                    # Format result data with company-focused structure
                    result_data = {
                        'Company_Number': company.get('company_number', ''),
                        'Company_Name': company.get('company_name', ''),
                        'Company_Tel': company.get('company_tel', ''),
                        'Company_Industry': company.get('company_industry', ''),
                        'Prefecture': company.get('prefecture', ''),
                        'URL_Name': url.get('url_name', ''),
                        'URL': url.get('url', ''),
                        'Content': url.get('content', '')[:500],  # Limit content length
                        'Matched_Terms': '|'.join(url.get('matched_terms', [])),
                        'ID': url.get('id', '')
                    }
                    
                    writer.writerow(result_data)
            
            # Get CSV content
            csv_content = output.getvalue()
            
            # Save to cache file with UTF-8 BOM for Excel compatibility
            with open(cache_file, 'w', encoding='utf-8-sig', newline='') as f:
                f.write(csv_content)
            
            return csv_content
            
        except Exception as e:
            # If error occurs, create a simple error CSV
            error_csv = f"Error,{str(e)}\n"
            with open(cache_file, 'w', encoding='utf-8-sig', newline='') as f:
                f.write(error_csv)
            return error_csv
    
    # Generate and cache the CSV
    generate_csv_content()
    
    # Generate filename for download
    timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
    filename = f"search_results_{timestamp}.csv"
    
    # Serve the newly created cached file
    return send_file(cache_file, as_attachment=True, download_name=filename)

