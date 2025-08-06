import os
from whoosh import fields, index
from whoosh.qparser import QueryParser
from whoosh.analysis import StandardAnalyzer
from typing import List, Dict

class WhooshSearchEngine:
    def __init__(self, index_dir: str = "data/index"):
        self.index_dir = index_dir
        self.schema = fields.Schema(
            id=fields.ID(stored=True, unique=True),
            title=fields.TEXT(stored=True),
            content=fields.TEXT(stored=True),
            url=fields.TEXT(stored=True)
        )
        self.ix = None
        self._setup_index()
    
    def _setup_index(self):
        if not os.path.exists(self.index_dir):
            os.makedirs(self.index_dir)
        
        if index.exists_in(self.index_dir):
            self.ix = index.open_dir(self.index_dir)
        else:
            self.ix = index.create_in(self.index_dir, self.schema)
    
    def add_document(self, doc_id: str, title: str, content: str, url: str = ""):
        writer = self.ix.writer()
        try:
            writer.add_document(
                id=doc_id,
                title=title,
                content=content,
                url=url
            )
            writer.commit()
        except Exception as e:
            writer.cancel()
            raise e
    
    def add_documents_batch(self, documents: List[Dict]):
        writer = self.ix.writer()
        try:
            for doc in documents:
                writer.add_document(
                    id=doc['id'],
                    title=doc['title'],
                    content=doc['content'],
                    url=doc.get('url', '')
                )
            writer.commit()
        except Exception as e:
            writer.cancel()
            raise e
    
    def search(self, query_string: str, limit: int = 10) -> List[Dict]:
        with self.ix.searcher() as searcher:
            parser = QueryParser("content", self.ix.schema)
            query = parser.parse(query_string)
            results = searcher.search(query, limit=limit)
            
            return [{
                'id': result['id'],
                'title': result['title'],
                'content': result['content'][:200] + '...' if len(result['content']) > 200 else result['content'],
                'url': result['url'],
                'score': result.score
            } for result in results]
    
    def search_in_title(self, query_string: str, limit: int = 10) -> List[Dict]:
        with self.ix.searcher() as searcher:
            parser = QueryParser("title", self.ix.schema)
            query = parser.parse(query_string)
            results = searcher.search(query, limit=limit)
            
            return [{
                'id': result['id'],
                'title': result['title'],
                'content': result['content'][:200] + '...' if len(result['content']) > 200 else result['content'],
                'url': result['url'],
                'score': result.score
            } for result in results]
    
    def clear_index(self):
        writer = self.ix.writer()
        writer.commit(mergetype=index.CLEAR)
    
    def get_document_count(self) -> int:
        with self.ix.searcher() as searcher:
            return searcher.doc_count_all()