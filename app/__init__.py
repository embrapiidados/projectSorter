from flask import Flask
from config import Config
import os

def create_app(config_class=Config):
    app = Flask(__name__)
    app.config.from_object(config_class)
    
    # Registrar blueprints
    from app.routes import main
    app.register_blueprint(main)
    
    # Garantir que a pasta de configuração existe
    os.makedirs('instance', exist_ok=True)
    
    # Verificar se a sincronização automática está habilitada
    if Config.get_auto_sync():
        with app.app_context():
            try:
                # Importar aqui para evitar importação circular
                from app.sync_manager import SyncManager
                import json
                
                # Criar gerenciador de sincronização
                sync_manager = SyncManager()
                
                # Conectar ao SharePoint usando credenciais do .env
                if sync_manager.connect_sharepoint():
                    # Baixar Excel e converter para JSON
                    print("Sincronização automática: Baixando dados do SharePoint...")
                    sync_manager.excel_to_json()
                    print("Sincronização automática concluída.")
            except Exception as e:
                print(f"Erro na sincronização automática: {str(e)}")
    
    return app
