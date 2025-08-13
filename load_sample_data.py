#!/usr/bin/env python3
"""
Load sample company data into the search index
This script loads comprehensive test data for development and testing
"""
import os
import sys
import json

# Add the project root to the path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from app.services.search_service import SearchService


def load_sample_companies():
    """Load sample company data from JSON file into search index"""
    print("🏢 Loading Sample Company Data into Search Index")
    print("=" * 60)
    
    # Initialize search service
    search_service = SearchService()
    
    # Load sample data from JSON file
    sample_data_path = "data/sample_companies.json"
    
    try:
        with open(sample_data_path, 'r', encoding='utf-8') as f:
            companies = json.load(f)
        print(f"📁 Loaded {len(companies)} companies from {sample_data_path}")
        
    except FileNotFoundError:
        print(f"❌ Error: {sample_data_path} not found")
        return False
    except json.JSONDecodeError as e:
        print(f"❌ Error parsing JSON: {e}")
        return False
    
    # Clear existing index
    print("🗑️  Clearing existing search index...")
    search_service.clear_index()
    
    # Add companies to search index
    print("📝 Adding companies to search index...")
    try:
        success = search_service.add_documents_batch(companies)
        if success:
            print("✅ Successfully added all companies to search index")
        else:
            print("❌ Failed to add companies to search index")
            return False
            
    except Exception as e:
        print(f"❌ Error adding companies: {e}")
        return False
    
    # Display statistics
    print("\n📊 Index Statistics:")
    print("-" * 30)
    stats = search_service.get_stats()
    print(f"📈 Total companies: {stats['total_documents']}")
    
    # Display prefecture distribution
    prefecture_counts = {}
    for company in companies:
        prefecture = company.get('prefecture', 'unknown')
        prefecture_counts[prefecture] = prefecture_counts.get(prefecture, 0) + 1
    
    print(f"🗾 Prefecture distribution:")
    for prefecture, count in sorted(prefecture_counts.items()):
        print(f"   {prefecture}: {count} companies")
    
    # Test search functionality
    print(f"\n🔍 Testing Search Functionality:")
    print("-" * 35)
    
    test_queries = [
        ("Python", "Programming language"),
        ("AI", "Artificial Intelligence"), 
        ("機械学習", "Machine Learning in Japanese"),
        ("IoT", "Internet of Things"),
        ("医療", "Medical/Healthcare"),
        ("製造業", "Manufacturing")
    ]
    
    for query, description in test_queries:
        results = search_service.search(query, limit=3)
        print(f"'{query}' ({description}): {results['total_found']} results")
        if results['results']:
            for result in results['results'][:2]:  # Show top 2
                print(f"  • {result['title']}")
    
    # Test prefecture filtering
    print(f"\n🏷️  Testing Prefecture Filtering:")
    print("-" * 37)
    
    prefecture_tests = [
        ("tokyo", "Tokyo companies"),
        ("osaka", "Osaka companies"), 
        ("fukuoka", "Fukuoka companies")
    ]
    
    for prefecture, description in prefecture_tests:
        results = search_service.search("開発", prefecture=prefecture, limit=5)
        print(f"{prefecture} '{description}': {results['total_found']} development companies")
    
    print(f"\n🎉 Sample data loading complete!")
    print(f"💡 You can now test the search engine with comprehensive data")
    print(f"🌐 Run the Flask app: uv run python run.py")
    
    return True


if __name__ == "__main__":
    success = load_sample_companies()
    if success:
        print(f"\n✅ Sample data loaded successfully!")
        sys.exit(0)
    else:
        print(f"\n❌ Failed to load sample data")
        sys.exit(1)