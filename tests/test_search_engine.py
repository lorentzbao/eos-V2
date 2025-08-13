#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.services.search_service import SearchService

def test_search_engine():
    print("=== 日本語検索エンジンテスト ===\n")
    
    # Initialize search service
    search_service = SearchService()
    
    # Test data - clean set with no duplicates
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
        },
        {
            "id": "doc4",
            "title": "データベース設計入門",
            "content": "リレーショナルデータベースの正規化やインデックスについて学習します。SQLクエリの最適化も重要です。",
            "url": "https://example.com/database-design"
        },
        {
            "id": "doc5",
            "title": "JavaScript 基本構文",
            "content": "JavaScriptはウェブブラウザで動作するスクリプト言語です。DOM操作やイベント処理が可能です。",
            "url": "https://example.com/javascript"
        },
        {
            "id": "doc6",
            "title": "モバイルアプリ開発",
            "content": "iOSやAndroidアプリの開発手法を紹介します。ユーザーインターフェースの設計が重要です。",
            "url": "https://example.com/mobile-dev"
        }
    ]
    
    print("1. インデックスをクリアしてテストデータを追加中...")
    try:
        # Clear existing index to avoid duplicates
        search_service.clear_index()
        search_service.add_documents_batch(test_documents)
        print("✓ インデックスのクリアとテストデータの追加が完了しました\n")
    except Exception as e:
        print(f"✗ エラー: {e}\n")
        return
    
    # Test queries
    test_queries = [
        "Python",
        "機械学習",
        "ウェブ開発",
        "title:Python",
        '"データ分析"',
        "Flask Django"
    ]
    
    print("2. 検索テスト開始...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"テスト {i}: '{query}'")
        print("-" * 50)
        
        try:
            results = search_service.search(query, limit=5)
            
            if results['results']:
                print(f"検索結果: {results['total_found']}件 ({results['search_time']}秒)")
                print(f"処理済みクエリ: {results['processed_query']}")
                print()
                
                for j, result in enumerate(results['results'][:3], 1):
                    print(f"  {j}. {result['title']} (スコア: {result['score']:.3f})")
                    print(f"     {result['content']}")
                    if result['url']:
                        print(f"     URL: {result['url']}")
                    print()
            else:
                print("検索結果がありません\n")
                
        except Exception as e:
            print(f"✗ 検索エラー: {e}\n")
        
        print("=" * 60)
        print()
    
    # Test stats
    print("3. 統計情報:")
    try:
        stats = search_service.get_stats()
        print(f"✓ インデックス済み文書数: {stats['total_documents']}件\n")
    except Exception as e:
        print(f"✗ 統計取得エラー: {e}\n")
    
    print("=== テスト完了 ===")

if __name__ == "__main__":
    test_search_engine()