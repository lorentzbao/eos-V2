from typing import List, Dict, Optional
from whoosh import fields, index
from whoosh.qparser import QueryParser, OrGroup
import os
from .tokenizers import get_tokenizer

class WhooshContractJapanese:
    """Whoosh search engine for contract data with district/branch/solicitor filtering"""

    def __init__(self, index_dir: str = "data/contract_indexes/A", tokenizer_type: Optional[str] = None, prewarm: bool = False):
        """
        Initialize Whoosh search engine for contract data.

        Args:
            index_dir: Directory to store the search index
            tokenizer_type: Type of tokenizer ('janome' or 'mecab', auto-detect if None)
            prewarm: Whether to prewarm the index on initialization
        """
        self.index_dir = index_dir
        self.tokenizer = get_tokenizer(tokenizer_type)
        self.prewarm = prewarm

        # Contract schema - includes all standard fields plus contract-specific fields
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

            # Contract-specific fields (契約モード用)
            DISTRICT_NAME=fields.KEYWORD(stored=True),  # 地域事業本部名
            MOTHERBRANCH_CD=fields.KEYWORD(stored=True),  # 支店コード
            BRANCH_NAME=fields.TEXT(stored=True),  # 支店名
            SOLICITOR_CD=fields.KEYWORD(stored=True),  # ソリシターコード
            SOLICITOR=fields.TEXT(stored=True),  # ソリシター名

            # Website information
            main_domain_url=fields.TEXT(stored=True),  # ホームページURL
            url_name=fields.TEXT(stored=True)  # URL description
        )

        self.ix = None
        self._setup_index()
        if self.prewarm:
            self._prewarm_index()

    def _setup_index(self):
        """Initialize or open existing index"""
        if not os.path.exists(self.index_dir):
            os.makedirs(self.index_dir)
            self.ix = index.create_in(self.index_dir, self.schema)
        else:
            try:
                self.ix = index.open_dir(self.index_dir)
            except index.EmptyIndexError:
                self.ix = index.create_in(self.index_dir, self.schema)

    def _prewarm_index(self):
        """Prewarm the index by opening a searcher (loads into memory)"""
        try:
            with self.ix.searcher() as searcher:
                # Just opening the searcher loads the index into memory
                pass
        except Exception as e:
            print(f"Warning: Failed to prewarm index: {e}")

    def _tokenize_japanese(self, text: str) -> str:
        """Tokenize Japanese text and return space-separated tokens"""
        if not text:
            return ""

        # Use the tokenizer's built-in filtering
        tokens = self.tokenizer.tokenize_and_filter(text, min_length=2)

        # Additional filtering for numeric tokens
        filtered_tokens = [
            token.lower().strip()
            for token in tokens
            if not token.isdigit()
        ]

        return " ".join(filtered_tokens)

    def add_documents_batch(self, documents: List[Dict]) -> bool:
        """Add multiple documents in a batch (more efficient than adding one by one)"""
        if not documents:
            return False

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

                    # Contract-specific fields
                    DISTRICT_NAME=doc.get('DISTRICT_NAME', ''),
                    MOTHERBRANCH_CD=doc.get('MOTHERBRANCH_CD', ''),
                    BRANCH_NAME=doc.get('BRANCH_NAME', ''),
                    SOLICITOR_CD=doc.get('SOLICITOR_CD', ''),
                    SOLICITOR=doc.get('SOLICITOR', ''),

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

    def search(self, query_string: str, limit: int = 10, branch_cd: str = "", solicitor_cd: str = "",
               sort_by: str = "", city: str = "") -> List[Dict]:
        """
        Search in content with branch and solicitor filtering

        Args:
            query_string: Search query
            limit: Maximum results
            branch_cd: MOTHERBRANCH_CD filter (支店コード)
            solicitor_cd: SOLICITOR_CD filter (ソリシターコード)
            sort_by: Sort method
            city: City filter
        """
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

                # Always filter for contract status (契約)
                from whoosh.query import Term
                filters.append(Term("CUST_STATUS2", "契約"))

                if branch_cd:
                    filters.append(Term("MOTHERBRANCH_CD", branch_cd))

                if solicitor_cd:
                    filters.append(Term("SOLICITOR_CD", solicitor_cd))

                if city:
                    filters.append(Term("city", city))

                # Combine filters with AND logic
                filter_query = None
                if filters:
                    from whoosh.query import And
                    filter_query = And(filters)

                # Execute search with sorting
                if sort_by == "revenue":
                    results = searcher.search(query, limit=limit, terms=True, filter=filter_query,
                                            sortedby="CURR_SETLMNT_TAKING_AMT", reverse=True)
                elif sort_by == "employees":
                    results = searcher.search(query, limit=limit, terms=True, filter=filter_query,
                                            sortedby="EMPLOYEE_ALL_NUM", reverse=True)
                else:
                    results = searcher.search(query, limit=limit, terms=True, filter=filter_query)

                # Convert results to list of dicts
                search_results = []
                for hit in results:
                    # Use Whoosh's built-in matched_terms() method and process the results
                    raw_matched_terms = hit.matched_terms()
                    # Extract unique terms from tuples and decode bytes
                    unique_terms = set()
                    for field_name, term_bytes in raw_matched_terms:
                        if isinstance(term_bytes, bytes):
                            term = term_bytes.decode('utf-8')
                        else:
                            term = str(term_bytes)
                        unique_terms.add(term)
                    matched_terms = list(unique_terms)

                    result = {
                        'id': hit['id'],
                        'url': hit['url'],
                        'score': hit.score,

                        # Corporate identification
                        'jcn': hit['jcn'],
                        'CUST_STATUS2': hit['CUST_STATUS2'],
                        'company_name_kj': hit['company_name_kj'],

                        # Address
                        'company_address_all': hit['company_address_all'],
                        'prefecture': hit['prefecture'],
                        'city': hit['city'],

                        # Industry
                        'LARGE_CLASS_NAME': hit['LARGE_CLASS_NAME'],
                        'MIDDLE_CLASS_NAME': hit['MIDDLE_CLASS_NAME'],

                        # Financial
                        'CURR_SETLMNT_TAKING_AMT': hit['CURR_SETLMNT_TAKING_AMT'],
                        'EMPLOYEE_ALL_NUM': hit['EMPLOYEE_ALL_NUM'],

                        # Organization
                        'district_finalized_cd': hit['district_finalized_cd'],
                        'branch_name_cd': hit['branch_name_cd'],

                        # Contract-specific
                        'DISTRICT_NAME': hit['DISTRICT_NAME'],
                        'MOTHERBRANCH_CD': hit['MOTHERBRANCH_CD'],
                        'BRANCH_NAME': hit['BRANCH_NAME'],
                        'SOLICITOR_CD': hit['SOLICITOR_CD'],
                        'SOLICITOR': hit['SOLICITOR'],

                        # Website
                        'main_domain_url': hit['main_domain_url'],
                        'url_name': hit['url_name'],

                        'matched_terms': matched_terms
                    }
                    search_results.append(result)

                return search_results

        except Exception as e:
            import traceback
            print(f"Search error: {e}")
            print(f"Traceback: {traceback.format_exc()}")
            return []

    def get_document_count(self) -> int:
        """Get total number of documents in the index"""
        try:
            with self.ix.searcher() as searcher:
                return searcher.doc_count_all()
        except:
            return 0

    def clear_index(self):
        """Clear all documents from the index"""
        try:
            writer = self.ix.writer()
            writer.commit(mergetype=index.CLEAR)
        except Exception as e:
            print(f"Error clearing index: {e}")

    def optimize_index(self):
        """Optimize the index for better search performance"""
        try:
            writer = self.ix.writer()
            writer.commit(optimize=True)
        except Exception as e:
            print(f"Error optimizing index: {e}")
