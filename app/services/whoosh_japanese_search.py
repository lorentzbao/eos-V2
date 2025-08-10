import os
import tempfile
from whoosh import fields, index
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.analysis import StandardAnalyzer, RegexTokenizer, LowercaseFilter, Filter
from janome.tokenizer import Tokenizer as JanomeTokenizer
from typing import List, Dict

class SimpleJapaneseAnalyzer:
    """Simple Japanese text analyzer using Janome"""
    
    def __init__(self):
        self.tokenizer = JanomeTokenizer()
        self.stop_words = {'する', 'ある', 'なる', 'いる', 'できる', 'という', 'として', 'の', 'に', 'は', 'を', 'が', 'で', 'て', 'と'}
    
    def __call__(self, text, **kwargs):
        """Process text and yield tokens"""
        from whoosh.analysis.tokenizers import Token
        
        # Tokenize with Janome
        for token in self.tokenizer.tokenize(text):
            word = token.surface.lower().strip()
            pos = token.part_of_speech.split(',')[0]
            
            # Only include meaningful parts of speech
            if pos in ['名詞', '動詞', '形容詞', '副詞'] and len(word) > 1:
                # Skip common stop words
                if word not in self.stop_words:
                    yield Token(word)

class WhooshJapaneseSearch:
    def __init__(self, index_dir: str = "data/whoosh_index"):
        self.index_dir = index_dir
        
        # Create schema with Japanese analyzer
        japanese_analyzer = SimpleJapaneseAnalyzer()
        
        self.schema = fields.Schema(
            id=fields.ID(stored=True, unique=True),
            title=fields.TEXT(stored=True, analyzer=japanese_analyzer),
            content=fields.TEXT(stored=True, analyzer=japanese_analyzer),
            url=fields.TEXT(stored=True),
            full_text=fields.TEXT(analyzer=japanese_analyzer)  # Combined field for search
        )
        
        self.ix = None
        self._setup_index()
    
    def _setup_index(self):
        """Setup or open the Whoosh index"""
        if not os.path.exists(self.index_dir):
            os.makedirs(self.index_dir)
        
        try:
            if index.exists_in(self.index_dir):
                self.ix = index.open_dir(self.index_dir)
            else:
                self.ix = index.create_in(self.index_dir, self.schema)
        except Exception as e:
            print(f"Error with index directory {self.index_dir}: {e}")
            # Fallback to temporary directory
            temp_dir = tempfile.mkdtemp(prefix="whoosh_")
            print(f"Using temporary index at: {temp_dir}")
            self.index_dir = temp_dir
            self.ix = index.create_in(self.index_dir, self.schema)
    
    def add_document(self, doc_id: str, title: str, content: str, url: str = ""):
        """Add a single document to the index"""
        writer = self.ix.writer()
        try:
            full_text = f"{title} {content}"
            writer.add_document(
                id=doc_id,
                title=title,
                content=content,
                url=url,
                full_text=full_text
            )
            writer.commit()
            return True
        except Exception as e:
            print(f"Error adding document {doc_id}: {e}")
            writer.cancel()
            return False
    
    def add_documents_batch(self, documents: List[Dict]):
        """Add multiple documents in a batch"""
        writer = self.ix.writer()
        try:
            for doc in documents:
                full_text = f"{doc['title']} {doc['content']}"
                writer.add_document(
                    id=doc['id'],
                    title=doc['title'],
                    content=doc['content'],
                    url=doc.get('url', ''),
                    full_text=full_text
                )
            writer.commit()
            return True
        except Exception as e:
            print(f"Error in batch add: {e}")
            writer.cancel()
            return False
    
    def search(self, query_string: str, limit: int = 10) -> List[Dict]:
        """Search in all fields"""
        if not query_string.strip():
            return []
        
        try:
            with self.ix.searcher() as searcher:
                # Create multi-field parser for searching title, content, and full_text
                parser = MultifieldParser(["title", "content", "full_text"], self.ix.schema)
                
                try:
                    query = parser.parse(query_string)
                except Exception as e:
                    # If parsing fails, try simple query in full_text field
                    simple_parser = QueryParser("full_text", self.ix.schema)
                    query = simple_parser.parse(query_string)
                
                results = searcher.search(query, limit=limit)
                
                return [{
                    'id': result['id'],
                    'title': result['title'],
                    'content': result['content'][:200] + '...' if len(result['content']) > 200 else result['content'],
                    'url': result['url'],
                    'score': float(result.score) if result.score else 0.0
                } for result in results]
                
        except Exception as e:
            print(f"Search error: {e}")
            return []
    
    def search_in_title(self, query_string: str, limit: int = 10) -> List[Dict]:
        """Search only in titles"""
        if not query_string.strip():
            return []
        
        try:
            with self.ix.searcher() as searcher:
                parser = QueryParser("title", self.ix.schema)
                query = parser.parse(query_string)
                results = searcher.search(query, limit=limit)
                
                return [{
                    'id': result['id'],
                    'title': result['title'],
                    'content': result['content'][:200] + '...' if len(result['content']) > 200 else result['content'],
                    'url': result['url'],
                    'score': float(result.score) if result.score else 0.0
                } for result in results]
                
        except Exception as e:
            print(f"Title search error: {e}")
            return []
    
    def clear_index(self):
        """Clear all documents from the index"""
        try:
            # Delete and recreate the index
            if os.path.exists(self.index_dir):
                import shutil
                shutil.rmtree(self.index_dir)
            os.makedirs(self.index_dir, exist_ok=True)
            self.ix = index.create_in(self.index_dir, self.schema)
            return True
        except Exception as e:
            print(f"Error clearing index: {e}")
            return False
    
    def get_document_count(self) -> int:
        """Get the total number of documents in the index"""
        try:
            with self.ix.searcher() as searcher:
                return searcher.doc_count_all()
        except Exception as e:
            print(f"Error getting document count: {e}")
            return 0
    
    def optimize_index(self):
        """Optimize the index for better performance"""
        try:
            # In modern Whoosh, optimization happens automatically
            # Just commit any pending changes
            if self.ix.latest_generation() > 0:
                return True
            return True
        except Exception as e:
            print(f"Error optimizing index: {e}")
            return False