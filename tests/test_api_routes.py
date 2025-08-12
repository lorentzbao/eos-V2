#!/usr/bin/env python3
"""
Test the separated API routes
"""
import json
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

def test_api_routes():
    """Test all API routes work correctly"""
    app = create_app()
    
    with app.test_client() as client:
        print("=== API Routes Test ===\n")
        
        # Test GET /api/stats
        print("1. Testing GET /api/stats")
        response = client.get('/api/stats')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Response: {data}")
        print()
        
        # Test POST /api/add_document
        print("2. Testing POST /api/add_document")
        test_doc = {
            "id": "api_test_1",
            "title": "API テストドキュメント",
            "content": "これはAPIルートのテスト用ドキュメントです。検索機能をテストします。",
            "url": "http://api-test.example.com"
        }
        
        response = client.post('/api/add_document', 
                             data=json.dumps(test_doc),
                             content_type='application/json')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Response: {data}")
        print()
        
        # Test POST /api/add_documents (batch)
        print("3. Testing POST /api/add_documents (batch)")
        batch_docs = {
            "documents": [
                {
                    "id": "api_test_2",
                    "title": "バッチテスト1",
                    "content": "バッチ追加テストの1つ目の文書です。",
                    "url": "http://batch1.example.com"
                },
                {
                    "id": "api_test_3", 
                    "title": "バッチテスト2",
                    "content": "バッチ追加テストの2つ目の文書です。",
                    "url": "http://batch2.example.com"
                }
            ]
        }
        
        response = client.post('/api/add_documents',
                             data=json.dumps(batch_docs),
                             content_type='application/json')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Response: {data}")
        print()
        
        # Test GET /api/search
        print("4. Testing GET /api/search")
        response = client.get('/api/search?q=テスト&limit=5')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Found {len(data.get('results', []))} results")
            for result in data.get('results', [])[:2]:  # Show first 2
                print(f"     - {result['title']} (score: {result['score']:.3f})")
        print()
        
        # Test GET /api/stats again (should show more documents)
        print("5. Testing GET /api/stats (after adding documents)")
        response = client.get('/api/stats')
        print(f"   Status: {response.status_code}")
        if response.status_code == 200:
            data = response.get_json()
            print(f"   Response: {data}")
        print()
        
        # Test web routes still work
        print("6. Testing web routes")
        response = client.get('/')
        print(f"   GET / Status: {response.status_code}")
        
        response = client.get('/search?q=テスト')
        print(f"   GET /search Status: {response.status_code}")
        print()
        
        print("=== Test Complete ===")

if __name__ == "__main__":
    test_api_routes()