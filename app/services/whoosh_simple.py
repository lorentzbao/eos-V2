import os
import shutil
from whoosh import fields, index
from whoosh.qparser import QueryParser, MultifieldParser, OrGroup
from whoosh.analysis import StandardAnalyzer
from janome.tokenizer import Tokenizer
from typing import List, Dict

class WhooshSimpleJapanese:
    """Whoosh search engine with pre-processed Japanese text"""
    
    def __init__(self, index_dir: str = "data/whoosh_index"):
        self.index_dir = index_dir
        self.tokenizer = Tokenizer()
        self.stop_words = {
            'する', 'ある', 'なる', 'いる', 'できる', 'という', 'として', 
            'の', 'に', 'は', 'を', 'が', 'で', 'て', 'と', 'から', 'まで',
            'だ', 'である', 'です', 'ます'
        }
        
        # Enterprise schema - lightweight with no raw content storage
        self.schema = fields.Schema(
            id=fields.ID(stored=True, unique=True),
            url=fields.TEXT(stored=True),
            content_tokens=fields.TEXT(),  # Pre-processed content (searchable only)
            
            # Enterprise corporate identification
            jcn=fields.KEYWORD(stored=True),  # 法人番号 (Corporate Number)
            CUST_STATUS2=fields.KEYWORD(stored=True),  # 顧客区分 (Customer Status)
            company_name_kj=fields.TEXT(stored=True),  # 漢字名 (Company Name - this is the title)
            
            # Address information
            company_address_all=fields.TEXT(stored=True),  # 住所 (Full Address)
            prefecture=fields.KEYWORD(stored=True, lowercase=True),  # 都道府県
            city=fields.KEYWORD(stored=True),  # 市区町村
            
            # Industry classification
            LARGE_CLASS_NAME=fields.KEYWORD(stored=True),  # 業種大分類
            MIDDLE_CLASS_NAME=fields.KEYWORD(stored=True),  # 業種中分類
            
            # Financial data
            CURR_SETLMNT_TAKING_AMT=fields.NUMERIC(stored=True),  # 売上高
            EMPLOYEE_ALL_NUM=fields.NUMERIC(stored=True),  # 従業員数
            
            # Organization codes
            district_finalized_cd=fields.KEYWORD(stored=True),  # 事業本部コード
            branch_name_cd=fields.KEYWORD(stored=True),  # 支店コード
            
            # Website information
            main_domain_url=fields.TEXT(stored=True),  # ホームページURL
            url_name=fields.TEXT(stored=True)  # URL description
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
                # Skip numeric tokens and pure digits
                if word.isdigit():
                    continue
                if word not in self.stop_words:
                    tokens.append(word)
        
        return ' '.join(tokens)
    
    def add_document(self, doc_id: str, url: str = "", content: str = "", 
                   jcn: str = "", CUST_STATUS2: str = "", company_name_kj: str = "",
                   company_address_all: str = "", prefecture: str = "", city: str = "",
                   LARGE_CLASS_NAME: str = "", MIDDLE_CLASS_NAME: str = "",
                   CURR_SETLMNT_TAKING_AMT: int = 0, EMPLOYEE_ALL_NUM: int = 0,
                   district_finalized_cd: str = "", branch_name_cd: str = "",
                   main_domain_url: str = "", url_name: str = ""):
        """Add a single document to the index with enterprise metadata"""
        try:
            # Pre-process Japanese text for content
            content_tokens = self._tokenize_japanese(content)
            
            writer = self.ix.writer()
            writer.add_document(
                id=doc_id,
                url=url,
                content_tokens=content_tokens,  # Content is searchable but not stored
                
                # Enterprise corporate identification
                jcn=jcn,
                CUST_STATUS2=CUST_STATUS2,
                company_name_kj=company_name_kj,
                
                # Address information
                company_address_all=company_address_all,
                prefecture=prefecture.lower() if prefecture else "",
                city=city,
                
                # Industry classification
                LARGE_CLASS_NAME=LARGE_CLASS_NAME,
                MIDDLE_CLASS_NAME=MIDDLE_CLASS_NAME,
                
                # Financial data
                CURR_SETLMNT_TAKING_AMT=CURR_SETLMNT_TAKING_AMT,
                EMPLOYEE_ALL_NUM=EMPLOYEE_ALL_NUM,
                
                # Organization codes
                district_finalized_cd=district_finalized_cd,
                branch_name_cd=branch_name_cd,
                
                # Website information
                main_domain_url=main_domain_url,
                url_name=url_name
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
                # Use pre-tokenized content if available, otherwise tokenize
                if 'content_tokens' in doc and doc['content_tokens']:
                    content_tokens = doc['content_tokens']
                elif 'content' in doc and doc['content']:
                    content_tokens = self._tokenize_japanese(doc['content'])
                else:
                    content_tokens = ""
                
                writer.add_document(
                    id=doc['id'],
                    url=doc.get('url', ''),
                    content_tokens=content_tokens,  # Content is searchable but not stored
                    
                    # Enterprise corporate identification
                    jcn=doc.get('jcn', ''),
                    CUST_STATUS2=doc.get('CUST_STATUS2', ''),
                    company_name_kj=doc.get('company_name_kj', ''),
                    
                    # Address information
                    company_address_all=doc.get('company_address_all', ''),
                    prefecture=doc.get('prefecture', '').lower() if doc.get('prefecture') else "",
                    city=doc.get('city', ''),
                    
                    # Industry classification
                    LARGE_CLASS_NAME=doc.get('LARGE_CLASS_NAME', ''),
                    MIDDLE_CLASS_NAME=doc.get('MIDDLE_CLASS_NAME', ''),
                    
                    # Financial data
                    CURR_SETLMNT_TAKING_AMT=doc.get('CURR_SETLMNT_TAKING_AMT', 0),
                    EMPLOYEE_ALL_NUM=doc.get('EMPLOYEE_ALL_NUM', 0),
                    
                    # Organization codes
                    district_finalized_cd=doc.get('district_finalized_cd', ''),
                    branch_name_cd=doc.get('branch_name_cd', ''),
                    
                    # Website information
                    main_domain_url=doc.get('main_domain_url', ''),
                    url_name=doc.get('url_name', '')
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
    
    def search(self, query_string: str, limit: int = 10, prefecture: str = "", cust_status: str = "", sort_by: str = "") -> List[Dict]:
        """Search in content only with highlighting support, prefecture and cust_status filtering, and sorting"""
        if not query_string.strip():
            return []
        
        try:
            # Pre-process the query
            processed_query = self._tokenize_japanese(query_string)
            if not processed_query:
                # Fallback to original query
                processed_query = query_string
            
            with self.ix.searcher() as searcher:
                # Search only in content tokens with OR logic for multiple terms
                parser = QueryParser("content_tokens", self.ix.schema, group=OrGroup)
                
                try:
                    query = parser.parse(processed_query)
                except Exception:
                    # Fallback to even simpler parsing
                    from whoosh.query import Or, Term
                    # Split terms and create OR query manually
                    terms = processed_query.split()
                    if len(terms) == 1:
                        query = Term("content_tokens", terms[0])
                    else:
                        query = Or([Term("content_tokens", term) for term in terms])
                
                # Build filters if specified
                filters = []
                if prefecture:
                    from whoosh.query import Term
                    filters.append(Term("prefecture", prefecture.lower()))
                
                if cust_status:
                    from whoosh.query import Term
                    filters.append(Term("CUST_STATUS2", cust_status))
                
                # Combine filters with AND logic
                filter_query = None
                if filters:
                    if len(filters) == 1:
                        filter_query = filters[0]
                    else:
                        from whoosh.query import And
                        filter_query = And(filters)
                
                # Add sorting if specified
                sort_facet = None
                if sort_by == "jcn":
                    from whoosh.sorting import FieldFacet
                    sort_facet = FieldFacet("jcn")
                
                results = searcher.search(query, limit=limit, terms=True, filter=filter_query, sortedby=sort_facet)
                
                search_results = []
                for result in results:
                    # Use Whoosh's built-in matched_terms() method and process the results
                    raw_matched_terms = result.matched_terms()
                    # Extract unique terms from tuples and decode bytes
                    unique_terms = set()
                    for field_name, term_bytes in raw_matched_terms:
                        if isinstance(term_bytes, bytes):
                            term = term_bytes.decode('utf-8')
                        else:
                            term = str(term_bytes)
                        unique_terms.add(term)
                    matched_terms = list(unique_terms)
                    
                    search_results.append({
                        'id': result['id'],
                        'url': result['url'],
                        'score': float(result.score) if result.score else 0.0,
                        'matched_terms': matched_terms,
                        
                        # Enterprise corporate identification
                        'jcn': result.get('jcn', ''),
                        'CUST_STATUS2': result.get('CUST_STATUS2', ''),
                        'company_name_kj': result.get('company_name_kj', ''),
                        
                        # Address information
                        'company_address_all': result.get('company_address_all', ''),
                        'prefecture': result.get('prefecture', ''),
                        'city': result.get('city', ''),
                        
                        # Industry classification
                        'LARGE_CLASS_NAME': result.get('LARGE_CLASS_NAME', ''),
                        'MIDDLE_CLASS_NAME': result.get('MIDDLE_CLASS_NAME', ''),
                        
                        # Financial data
                        'CURR_SETLMNT_TAKING_AMT': result.get('CURR_SETLMNT_TAKING_AMT', ''),
                        'EMPLOYEE_ALL_NUM': result.get('EMPLOYEE_ALL_NUM', ''),
                        
                        # Organization codes
                        'district_finalized_cd': result.get('district_finalized_cd', ''),
                        'branch_name_cd': result.get('branch_name_cd', ''),
                        
                        # Website information
                        'main_domain_url': result.get('main_domain_url', ''),
                        'url_name': result.get('url_name', '')
                    })
                
                return search_results
                
        except Exception as e:
            print(f"Search error: {e}")
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
    
    def delete_document(self, doc_id: str) -> bool:
        """Delete a document by ID"""
        try:
            writer = self.ix.writer()
            # Delete document with the given ID
            deleted_count = writer.delete_by_term('id', doc_id)
            writer.commit()
            
            print(f"Deleted {deleted_count} document(s) with ID: {doc_id}")
            return deleted_count > 0
            
        except Exception as e:
            print(f"Error deleting document {doc_id}: {e}")
            return False