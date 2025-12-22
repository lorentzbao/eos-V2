from flask import Flask
import os
from datetime import timedelta
from omegaconf import DictConfig

def create_app(config: DictConfig = None):
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')

    # Use config if provided, otherwise use defaults
    if config:
        app.config['SECRET_KEY'] = config.app.secret_key
        # Configure session lifetime
        session_hours = config.app.get('session_lifetime_hours', 8)
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=session_hours)
        # Store search configuration
        if hasattr(config, 'search'):
            app.config['SEARCH_DEFAULT_LIMIT'] = config.search.get('default_limit', 100)
            app.config['CSV_OUTPUT_DIR'] = config.search.get('csv_output_dir', 'data/csv_output')
            app.config['CSV_ENABLE_BROWSER_DOWNLOAD'] = config.search.get('csv_enable_browser_download', True)
            app.config['PREWARM_INDEXES'] = config.search.get('prewarm_indexes', False)
        else:
            app.config['SEARCH_DEFAULT_LIMIT'] = 100
            app.config['CSV_OUTPUT_DIR'] = 'data/csv_output'
            app.config['CSV_ENABLE_BROWSER_DOWNLOAD'] = True
            app.config['PREWARM_INDEXES'] = False
        # Store multi-index configuration
        if hasattr(config, 'indexes'):
            app.config['INDEXES'] = config.indexes
        # Fallback to single index if indexes not defined
        elif hasattr(config, 'index'):
            app.config['INDEX_DIR'] = config.index.dir
    else:
        app.config['SECRET_KEY'] = 'your-secret-key-here'
        app.config['INDEX_DIR'] = 'data/whoosh_index'
        app.config['SEARCH_DEFAULT_LIMIT'] = 100
        app.config['CSV_OUTPUT_DIR'] = 'data/csv_output'
        app.config['CSV_ENABLE_BROWSER_DOWNLOAD'] = True
        app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(hours=8)

    # Initialize search service ONCE (for cache reuse)
    from app.services.search_service_prefecture import SearchServicePrefecture
    from app.services.multi_prefecture_search_service import MultiPrefectureSearchService
    from app.services.multi_contract_search_service import MultiContractSearchService

    prewarm = app.config.get('PREWARM_INDEXES', False)

    if 'INDEXES' in app.config:
        app.search_service = MultiPrefectureSearchService(app.config['INDEXES'], prewarm=prewarm)
    else:
        index_dir = app.config.get('INDEX_DIR', 'data/whoosh_index')
        app.search_service = SearchServicePrefecture(index_dir, prewarm=prewarm)

    # Initialize contract search service
    if hasattr(config, 'contract_indexes'):
        app.config['CONTRACT_INDEXES'] = config.contract_indexes
        app.contract_search_service = MultiContractSearchService(app.config['CONTRACT_INDEXES'], prewarm=prewarm)
    else:
        app.contract_search_service = None

    # Register blueprints
    from app.routes.main import main
    from app.routes.api import api

    app.register_blueprint(main)
    app.register_blueprint(api)

    return app