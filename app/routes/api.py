from flask import Blueprint, request, jsonify, session, send_file, current_app
from app.services.search_service import SearchService
import csv
import io
import os
import hashlib
from datetime import datetime

api = Blueprint('api', __name__, url_prefix='/api')

def get_search_service():
    """Get SearchService with configured index directory"""
    index_dir = current_app.config.get('INDEX_DIR', 'data/whoosh_index')
    return SearchService(index_dir)

@api.route('/search')
def api_search():
    """API endpoint for search queries"""
    query = request.args.get('q', '')
    limit = int(request.args.get('limit', 10))
    prefecture = request.args.get('prefecture', '')
    cust_status = request.args.get('cust_status', '')
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    results = get_search_service().search(query, limit, prefecture, cust_status)
    return jsonify(results)

@api.route('/add_document', methods=['POST'])
def api_add_document():
    """API endpoint to add a single document"""
    data = request.get_json()
    
    if not data or not all(k in data for k in ['id', 'title', 'content']):
        return jsonify({'error': 'Missing required fields: id, title, content'}), 400
    
    try:
        success = get_search_service().add_document(
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
        success = get_search_service().add_documents_batch(documents)
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
    return jsonify(get_search_service().get_stats())

@api.route('/clear_index', methods=['POST'])
def api_clear_index():
    """API endpoint to clear the search index"""
    try:
        success = get_search_service().clear_index()
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
        success = get_search_service().optimize_index()
        if success:
            return jsonify({'success': True, 'message': 'Index optimized successfully'})
        else:
            return jsonify({'error': 'Failed to optimize index'}), 500
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def get_cache_key(query, prefecture, cust_status):
    """Generate unique cache key for search parameters"""
    params = f"{query}:{prefecture}:{cust_status}"
    return hashlib.md5(params.encode('utf-8')).hexdigest()

@api.route('/download-csv')
def download_csv():
    """Download search results as CSV with file-based caching"""
    # Check authentication
    if 'username' not in session:
        return jsonify({'error': 'Authentication required'}), 401
    
    # Get search parameters
    query = request.args.get('q', '').strip()
    prefecture = request.args.get('prefecture', '')
    cust_status = request.args.get('cust_status', '')
    
    if not query:
        return jsonify({'error': 'Query parameter required'}), 400
    
    # Generate cache key and file path
    cache_key = get_cache_key(query, prefecture, cust_status)
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
            
            # Create CSV writer with enterprise data field order
            fieldnames = [
                'jcn', 'CUST_STATUS2', 'company_name_kj', 'company_address_all', 
                'LARGE_CLASS_NAME', 'MIDDLE_CLASS_NAME', 'CURR_SETLMNT_TAKING_AMT', 'EMPLOYEE_ALL_NUM',
                'prefecture', 'city', 'district_finalized_cd', 'branch_name_cd', 
                'main_domain_url', 'url_name', 'url', 'content', 'matched_terms', 'id'
            ]
            writer = csv.DictWriter(output, fieldnames=fieldnames)
            
            # Write header
            writer.writeheader()
            
            # Single search to get all results - most efficient approach with JCN sorting
            search_results = get_search_service().search(query, limit=10000, prefecture=prefecture, cust_status=cust_status, sort_by="jcn")
            grouped_results = search_results.get('grouped_results', [])
            
            # Write all results by flattening grouped results
            for company in grouped_results:
                for url in company.get('urls', []):
                    # Format result data with enterprise structure
                    result_data = {
                        'jcn': company.get('jcn', ''),
                        'CUST_STATUS2': company.get('CUST_STATUS2', ''),
                        'company_name_kj': company.get('company_name_kj', ''),
                        'company_address_all': company.get('company_address_all', ''),
                        'LARGE_CLASS_NAME': company.get('LARGE_CLASS_NAME', ''),
                        'MIDDLE_CLASS_NAME': company.get('MIDDLE_CLASS_NAME', ''),
                        'CURR_SETLMNT_TAKING_AMT': company.get('CURR_SETLMNT_TAKING_AMT', ''),
                        'EMPLOYEE_ALL_NUM': company.get('EMPLOYEE_ALL_NUM', ''),
                        'prefecture': company.get('prefecture', ''),
                        'city': company.get('city', ''),
                        'district_finalized_cd': company.get('district_finalized_cd', ''),
                        'branch_name_cd': company.get('branch_name_cd', ''),
                        'main_domain_url': company.get('main_domain_url', ''),
                        'url_name': url.get('url_name', ''),
                        'url': url.get('url', ''),
                        'content': url.get('content', '')[:500],  # Limit content length
                        'matched_terms': '|'.join(url.get('matched_terms', [])),
                        'id': url.get('id', '')
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

