#!/usr/bin/env python3
"""
Compare the custom implementation vs Whoosh implementation
"""
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.search_service import SearchService  # Custom implementation
from app.services.search_service_whoosh import WhooshSearchService  # Whoosh implementation

def compare_implementations():
    print("=== 検索エンジン実装比較テスト ===\n")
    
    # Test data
    test_documents = [
        {
            "id": "doc1",
            "title": "Python プログラミング入門",
            "content": "Pythonは初心者にも学びやすいプログラミング言語です。データ分析やウェブ開発に広く使われています。",
            "url": "https://example.com/python"
        },
        {
            "id": "doc2", 
            "title": "機械学習の基礎",
            "content": "機械学習はAIの重要な分野です。データからパターンを学習し、予測を行います。Python、R、TensorFlowなどのツールが使われます。",
            "url": "https://example.com/ml"
        },
        {
            "id": "doc3",
            "title": "ウェブ開発フレームワーク",
            "content": "FlaskやDjangoはPythonのウェブフレームワークです。APIの作成やウェブアプリケーションの開発に使用されます。",
            "url": "https://example.com/web"
        }
    ]
    
    # Initialize both search engines
    print("1. 検索エンジンを初期化中...")
    custom_search = SearchService()
    whoosh_search = WhooshSearchService()
    
    # Add test data to both
    print("2. テストデータを追加中...")
    custom_search.add_documents_batch(test_documents)
    whoosh_search.add_documents_batch(test_documents)
    
    print(f"カスタム実装: {custom_search.get_stats()['total_documents']}件")
    print(f"Whoosh実装: {whoosh_search.get_stats()['total_documents']}件\n")
    
    # Test queries
    test_queries = ["Python", "機械学習", "ウェブ開発"]
    
    for query in test_queries:
        print(f"クエリ: '{query}'")
        print("=" * 60)
        
        # Custom implementation results
        print("カスタム実装の結果:")
        custom_results = custom_search.search(query, limit=5)
        if custom_results['results']:
            for i, result in enumerate(custom_results['results'], 1):
                print(f"  {i}. {result['title']} (スコア: {result['score']:.3f})")
        else:
            print("  結果なし")
        print(f"  検索時間: {custom_results['search_time']}秒\n")
        
        # Whoosh implementation results
        print("Whoosh実装の結果:")
        whoosh_results = whoosh_search.search(query, limit=5)
        if whoosh_results['results']:
            for i, result in enumerate(whoosh_results['results'], 1):
                print(f"  {i}. {result['title']} (スコア: {result['score']:.3f})")
        else:
            print("  結果なし")
        print(f"  検索時間: {whoosh_results['search_time']}秒\n")
        
        print("-" * 60)
        print()
    
    print("=== 比較テスト完了 ===")
    print("\n実装の特徴:")
    print("カスタム実装:")
    print("  ✓ 軽量でシンプル")
    print("  ✓ JSONベースの永続化")
    print("  ✓ カスタムTF-IDFスコアリング")
    print("  ✓ 完全な制御と理解")
    
    print("\nWhoosh実装:")
    print("  ✓ 業界標準のライブラリ")
    print("  ✓ 高性能なインデックス")
    print("  ✓ 豊富な検索機能")
    print("  ✓ スケーラビリティ")

if __name__ == "__main__":
    compare_implementations()