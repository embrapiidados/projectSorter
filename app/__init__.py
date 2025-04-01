from flask import Flask
from config import Config

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Registrar blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    # Garantir que a pasta de configuração existe
    import os
    os.makedirs('instance', exist_ok=True)
    
    return app