#!/usr/bin/env python3
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.whoosh_simple import WhooshSimpleJapanese

def test_whoosh_simple():
    print("=== Whoosh Simple 日本語検索テスト ===\n")
    
    # Initialize search engine
    search_engine = WhooshSimpleJapanese()
    
    # Clear existing index
    print("既存のインデックスをクリア中...")
    search_engine.clear_index()
    
    # Test data
    test_documents = [
        {
            "id": "doc1",
            "title": "Python プログラミング入門",
            "content": "Pythonは初心者にも学びやすいプログラミング言語です。データ分析やウェブ開発に広く使われています。オブジェクト指向プログラミングをサポートし、豊富なライブラリが利用できます。",
            "url": "https://example.com/python"
        },
        {
            "id": "doc2", 
            "title": "機械学習の基礎知識",
            "content": "機械学習はAIの重要な分野です。データからパターンを学習し、予測を行います。Python、R、TensorFlowなどのツールが使われます。教師あり学習、教師なし学習、強化学習の3つの主要な分類があります。",
            "url": "https://example.com/ml"
        },
        {
            "id": "doc3",
            "title": "ウェブ開発フレームワーク比較",
            "content": "FlaskやDjangoはPythonのウェブフレームワークです。APIの作成やウェブアプリケーションの開発に使用されます。Flaskは軽量で柔軟性が高く、Djangoは機能が豊富で大規模開発に適しています。",
            "url": "https://example.com/web"
        },
        {
            "id": "doc4",
            "title": "データベース設計の原則",
            "content": "リレーショナルデータベースの設計は重要なスキルです。SQLを使ってデータの操作を行います。正規化、インデックス、制約などの概念を理解することが必要です。PostgreSQL、MySQL、SQLiteなどが一般的です。",
            "url": "https://example.com/db"
        },
        {
            "id": "doc5",
            "title": "人工知能と深層学習",
            "content": "深層学習は人工知能の最新技術です。ニューラルネットワークを使って複雑なパターンを学習します。画像認識、自然言語処理、音声認識などの分野で大きな成果を上げています。",
            "url": "https://example.com/ai"
        }
    ]
    
    print("1. テストデータを追加中...")
    success = search_engine.add_documents_batch(test_documents)
    if success:
        print("✓ テストデータの追加が完了しました")
    else:
        print("✗ テストデータの追加に失敗しました")
        return
    
    print(f"インデックス済み文書数: {search_engine.get_document_count()}件\n")
    
    # Test queries
    test_queries = [
        "Python",
        "機械学習",
        "ウェブ開発",  
        "データベース",
        "人工知能",
        "プログラミング",
        "Flask Django",
        "深層学習"
    ]
    
    print("2. 検索テスト開始...\n")
    
    for i, query in enumerate(test_queries, 1):
        print(f"テスト {i}: '{query}'")
        print("-" * 60)
        
        results = search_engine.search(query, limit=5)
        
        if results:
            print(f"検索結果: {len(results)}件")
            print()
            
            for j, result in enumerate(results, 1):
                print(f"  {j}. {result['title']} (スコア: {result['score']:.3f})")
                print(f"     {result['content']}")
                if result['url']:
                    print(f"     URL: {result['url']}")
                print()
        else:
            print("検索結果がありません\n")
        
        print("=" * 70)
        print()
    
    # Test title-only search
    print("3. タイトル検索テスト...")
    print("-" * 60)
    
    title_queries = ["Python", "機械学習", "ウェブ"]
    
    for query in title_queries:
        print(f"タイトル検索: '{query}'")
        results = search_engine.search_in_title(query, limit=3)
        if results:
            for result in results:
                print(f"  - {result['title']} (スコア: {result['score']:.3f})")
        else:
            print("  検索結果なし")
        print()
    
    print(f"最終統計: {search_engine.get_document_count()}件の文書がインデックス済み")
    print("=== Whoosh Simple テスト完了 ===")

if __name__ == "__main__":
    test_whoosh_simple()