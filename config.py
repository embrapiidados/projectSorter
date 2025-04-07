import os
import json
from dotenv import load_dotenv

load_dotenv(override=True)

class Config:
    SECRET_KEY = os.environ.get('SECRET_KEY') or 'chave-secreta-temporaria'
    OPENAI_API_KEY = os.environ.get('OPENAI_API_KEY') or 'your-api-key-here'
    
    # Caminho do arquivo Excel no SharePoint
    SHAREPOINT_EXCEL_PATH = os.environ.get('SHAREPOINT_EXCEL_PATH') or 'General/Lucas Pinheiro/db_classificacao/db_classificacao_projeto.xlsx'
    
    # Configurações que serão armazenadas localmente
    CONFIG_FILE = os.path.join('instance', 'config.json')
    
    @staticmethod
    def get_openai_api_key():
        try:
            if os.path.exists(Config.CONFIG_FILE):
                with open(Config.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    return config.get('OPENAI_API_KEY', '')
        except Exception as e:
            print(f"Erro ao carregar configuração: {e}")
        return ''
    
    @staticmethod
    def save_openai_api_key(api_key):
        try:
            config = {}
            if os.path.exists(Config.CONFIG_FILE):
                with open(Config.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    
            config['OPENAI_API_KEY'] = api_key
            
            with open(Config.CONFIG_FILE, 'w') as f:
                json.dump(config, f)
            return True
        except Exception as e:
            print(f"Erro ao salvar configuração: {e}")
            return False
    
    @staticmethod
    def get_auto_sync():
        """Obtém a configuração de sincronização automática."""
        try:
            if os.path.exists(Config.CONFIG_FILE):
                with open(Config.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    return config.get('auto_sync', False)
        except Exception as e:
            print(f"Erro ao carregar configuração de sincronização: {e}")
        return False
    
    @staticmethod
    def save_auto_sync(auto_sync):
        """Salva a configuração de sincronização automática."""
        try:
            config = {}
            if os.path.exists(Config.CONFIG_FILE):
                with open(Config.CONFIG_FILE, 'r') as f:
                    config = json.load(f)
                    
            config['auto_sync'] = auto_sync
            
            with open(Config.CONFIG_FILE, 'w') as f:
                json.dump(config, f)
            return True
        except Exception as e:
            print(f"Erro ao salvar configuração de sincronização: {e}")
            return False
