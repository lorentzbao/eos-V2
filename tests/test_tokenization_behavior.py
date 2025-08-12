#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.simple_search import SimpleJapaneseSearch

def test_tokenization_behavior():
    print("=== トークン化動作テスト ===\n")
    
    search_engine = SimpleJapaneseSearch()
    
    # Test documents
    test_docs = [
        {
            "id": "doc1",
            "title": "機械学習の基礎",
            "content": "機械学習は人工知能の重要な分野です。",
            "url": ""
        },
        {
            "id": "doc2", 
            "title": "学習方法について",
            "content": "効果的な学習には機械的な反復が重要です。",
            "url": ""
        },
        {
            "id": "doc3",
            "title": "産業機械の話",
            "content": "工場では様々な機械が使用されています。",
            "url": ""
        }
    ]
    
    # Add documents
    search_engine.add_documents_batch(test_docs)
    
    print("追加された文書:")
    for doc in test_docs:
        tokens = search_engine.tokenize_japanese(doc['title'] + ' ' + doc['content'])
        print(f"  {doc['title']}: {tokens}")
    print()
    
    # Test different query approaches
    queries = [
        "機械学習",      # Original compound
        "機械 学習",     # Space-separated  
        "学習",          # Single term
        "機械"           # Single term
    ]
    
    for query in queries:
        print(f"クエリ: '{query}'")
        tokens = search_engine.tokenize_japanese(query)
        print(f"トークン化: {tokens}")
        
        results = search_engine.search(query, limit=5)
        print("検索結果:")
        
        if results:
            for i, result in enumerate(results, 1):
                print(f"  {i}. {result['title']} (スコア: {result['score']:.3f})")
        else:
            print("  結果なし")
        print("-" * 50)
        print()

if __name__ == "__main__":
    test_tokenization_behavior()