from flask import Flask
import os
from omegaconf import DictConfig

def create_app(config: DictConfig = None):
    app = Flask(__name__,
                template_folder='../templates',
                static_folder='../static')

    # Use config if provided, otherwise use defaults
    if config:
        app.config['SECRET_KEY'] = config.app.secret_key
        # Store multi-index configuration
        if hasattr(config, 'indexes'):
            app.config['INDEXES'] = config.indexes
        # Fallback to single index if indexes not defined
        elif hasattr(config, 'index'):
            app.config['INDEX_DIR'] = config.index.dir
    else:
        app.config['SECRET_KEY'] = 'your-secret-key-here'
        app.config['INDEX_DIR'] = 'data/whoosh_index'

    # Initialize search service ONCE (for cache reuse)
    from app.services.search_service import SearchService
    from app.services.multi_index_search_service import MultiIndexSearchService

    if 'INDEXES' in app.config:
        app.search_service = MultiIndexSearchService(app.config['INDEXES'])
    else:
        index_dir = app.config.get('INDEX_DIR', 'data/whoosh_index')
        app.search_service = SearchService(index_dir)

    # Register blueprints
    from app.routes.main import main
    from app.routes.api import api

    app.register_blueprint(main)
    app.register_blueprint(api)

    return app