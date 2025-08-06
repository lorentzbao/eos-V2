from flask import Flask
import os

def create_app():
    app = Flask(__name__, 
                template_folder='../templates',
                static_folder='../static')
    app.config['SECRET_KEY'] = 'your-secret-key-here'
    
    from app.routes.main import main
    app.register_blueprint(main)
    
    return app