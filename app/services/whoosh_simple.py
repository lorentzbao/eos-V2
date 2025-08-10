import os
import shutil
from whoosh import fields, index
from whoosh.qparser import QueryParser, MultifieldParser
from whoosh.analysis import StandardAnalyzer
from janome.tokenizer import Tokenizer
from typing import List, Dict

class WhooshSimpleJapanese:
    """Whoosh search engine with pre-processed Japanese text"""
    
    def __init__(self, index_dir: str = "data/whoosh_simple"):
        self.index_dir = index_dir
        self.tokenizer = Tokenizer()
        self.stop_words = {
            'する', 'ある', 'なる', 'いる', 'できる', 'という', 'として', 
            'の', 'に', 'は', 'を', 'が', 'で', 'て', 'と', 'から', 'まで',
            'だ', 'である', 'です', 'ます'
        }
        
        # Simple schema without custom analyzers
        self.schema = fields.Schema(
            id=fields.ID(stored=True, unique=True),
            title=fields.TEXT(stored=True),
            content=fields.TEXT(stored=True),
            url=fields.TEXT(stored=True),
            title_tokens=fields.TEXT(),  # Pre-processed title
            content_tokens=fields.TEXT()  # Pre-processed content
        )
        
        self.ix = None
        self._setup_index()
    
    def _setup_index(self):
        """Setup or create the Whoosh index"""
        try:
            if not os.path.exists(self.index_dir):
                os.makedirs(self.index_dir)
            
            if index.exists_in(self.index_dir):
                self.ix = index.open_dir(self.index_dir)
            else:
                self.ix = index.create_in(self.index_dir, self.schema)
                
        except Exception as e:
            print(f"Error setting up index: {e}")
            # Try to clear and recreate
            try:
                if os.path.exists(self.index_dir):
                    shutil.rmtree(self.index_dir)
                os.makedirs(self.index_dir)
                self.ix = index.create_in(self.index_dir, self.schema)
            except Exception as e2:
                print(f"Failed to recreate index: {e2}")
                raise e2
    
    def _tokenize_japanese(self, text: str) -> str:
        """Tokenize Japanese text and return space-separated tokens"""
        if not text:
            return ""
        
        tokens = []
        for token in self.tokenizer.tokenize(text):
            word = token.surface.lower().strip()
            pos = token.part_of_speech.split(',')[0]
            
            # Include meaningful parts of speech
            if pos in ['名詞', '動詞', '形容詞', '副詞'] and len(word) > 1:
                if word not in self.stop_words:
                    tokens.append(word)
        
        return ' '.join(tokens)
    
    def add_document(self, doc_id: str, title: str, content: str, url: str = ""):
        """Add a single document to the index"""
        try:
            # Pre-process Japanese text
            title_tokens = self._tokenize_japanese(title)
            content_tokens = self._tokenize_japanese(content)
            
            writer = self.ix.writer()
            writer.add_document(
                id=doc_id,
                title=title,
                content=content,
                url=url,
                title_tokens=title_tokens,
                content_tokens=content_tokens
            )
            writer.commit()
            return True
            
        except Exception as e:
            print(f"Error adding document {doc_id}: {e}")
            try:
                writer.cancel()
            except:
                pass
            return False
    
    def add_documents_batch(self, documents: List[Dict]):
        """Add multiple documents in a batch"""
        try:
            writer = self.ix.writer()
            
            for doc in documents:
                # Pre-process Japanese text
                title_tokens = self._tokenize_japanese(doc['title'])
                content_tokens = self._tokenize_japanese(doc['content'])
                
                writer.add_document(
                    id=doc['id'],
                    title=doc['title'],
                    content=doc['content'],
                    url=doc.get('url', ''),
                    title_tokens=title_tokens,
                    content_tokens=content_tokens
                )
            
            writer.commit()
            return True
            
        except Exception as e:
            print(f"Error in batch add: {e}")
            try:
                writer.cancel()
            except:
                pass
            return False
    
    def search(self, query_string: str, limit: int = 10) -> List[Dict]:
        """Search in title and content"""
        if not query_string.strip():
            return []
        
        try:
            # Pre-process the query
            processed_query = self._tokenize_japanese(query_string)
            if not processed_query:
                # Fallback to original query
                processed_query = query_string
            
            with self.ix.searcher() as searcher:
                # Search in both original and tokenized fields
                parser = MultifieldParser(["title", "content", "title_tokens", "content_tokens"], self.ix.schema)
                
                try:
                    query = parser.parse(processed_query)
                except Exception:
                    # Fallback to simple search
                    simple_parser = QueryParser("content_tokens", self.ix.schema)
                    query = simple_parser.parse(processed_query)
                
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
            # Pre-process the query
            processed_query = self._tokenize_japanese(query_string)
            if not processed_query:
                processed_query = query_string
            
            with self.ix.searcher() as searcher:
                # Search in both title and title_tokens
                parser = MultifieldParser(["title", "title_tokens"], self.ix.schema)
                
                try:
                    query = parser.parse(processed_query)
                except Exception:
                    simple_parser = QueryParser("title_tokens", self.ix.schema)
                    query = simple_parser.parse(processed_query)
                
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
            if os.path.exists(self.index_dir):
                shutil.rmtree(self.index_dir)
            os.makedirs(self.index_dir)
            self.ix = index.create_in(self.index_dir, self.schema)
            return True
        except Exception as e:
            print(f"Error clearing index: {e}")
            return False
    
    def get_document_count(self) -> int:
        """Get the total number of documents"""
        try:
            with self.ix.searcher() as searcher:
                return searcher.doc_count_all()
        except Exception as e:
            print(f"Error getting document count: {e}")
            return 0
    
    def optimize_index(self):
        """Optimize the index (automatic in modern Whoosh)"""
        return True