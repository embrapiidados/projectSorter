import os
import json
import pandas as pd
import io
from datetime import datetime
from app.sharepoint_client import SharePointClient
from app.json_data_client import JsonDataClient
from config import Config
import logging
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv(override=True)

# Configure logging
logging.basicConfig(level=logging.INFO, 
                   format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger('sync_manager')

class SyncManager:
    """
    Gerencia a sincronização bidirecional entre arquivos JSON locais e planilhas Excel no SharePoint.
    """
    
    def __init__(self, sharepoint_client=None):
        """
        Inicializa o gerenciador de sincronização.
        
        Args:
            sharepoint_client: Cliente SharePoint opcional. Se não fornecido, será criado a partir das configurações.
        """
        self.json_client = JsonDataClient()
        self.sharepoint_client = sharepoint_client
        self.excel_path = Config.SHAREPOINT_EXCEL_PATH
        self.data_dir = 'app/data'
        
    def connect_sharepoint(self, username=None, password=None, site_url=None):
        """
        Conecta ao SharePoint usando as credenciais fornecidas ou do arquivo .env.
        
        Args:
            username: Nome de usuário do SharePoint (opcional, usa .env se não fornecido)
            password: Senha do SharePoint (opcional, usa .env se não fornecido)
            site_url: URL do site do SharePoint (opcional, usa .env se não fornecido)
            
        Returns:
            bool: True se a conexão for bem-sucedida
        """
        try:
            # Usar credenciais do .env se não fornecidas
            username = username or os.environ.get('sharepoint_email')
            password = password or os.environ.get('sharepoint_password')
            site_url = site_url or os.environ.get('sharepoint_url_site')
            
            if not all([username, password, site_url]):
                logger.error("Credenciais do SharePoint incompletas")
                return False
                
            self.sharepoint_client = SharePointClient(site_url, username, password)
            return True
        except Exception as e:
            logger.error(f"Erro ao conectar ao SharePoint: {str(e)}")
            return False
    
    def json_to_excel(self):
        """
        Converte os arquivos JSON locais para Excel e faz upload para o SharePoint.
        
        Returns:
            dict: Resultado da operação com status e mensagem
        """
        try:
            if not self.sharepoint_client:
                return {"success": False, "message": "Cliente SharePoint não inicializado"}
            
            # Carregar dados dos arquivos JSON
            all_projetos_path = os.path.join(self.data_dir, 'all_projetos.json')
            categorias_path = os.path.join(self.data_dir, 'categorias.json')
            logs_path = os.path.join(self.data_dir, 'logs.json')
            
            with open(all_projetos_path, 'r', encoding='utf-8') as f:
                projetos = json.load(f)
            
            with open(categorias_path, 'r', encoding='utf-8') as f:
                categorias = json.load(f)
            
            with open(logs_path, 'r', encoding='utf-8') as f:
                logs = json.load(f)
            
            # Criar DataFrames
            df_projetos = pd.DataFrame(projetos)
            df_categorias = pd.DataFrame(categorias)
            df_logs = pd.DataFrame(logs)
            
            # Criar um buffer para o arquivo Excel
            output = io.BytesIO()
            
            # Criar um escritor Excel
            with pd.ExcelWriter(output, engine='openpyxl') as writer:
                df_projetos.to_excel(writer, sheet_name='projetos', index=False)
                df_categorias.to_excel(writer, sheet_name='categorias', index=False)
                df_logs.to_excel(writer, sheet_name='logs', index=False)
            
            # Obter o conteúdo do buffer
            output.seek(0)
            excel_content = output.getvalue()
            
            # Fazer upload para o SharePoint
            self.sharepoint_client.upload_file(excel_content, self.excel_path)
            
            # Registrar timestamp da sincronização
            self._save_sync_timestamp('upload')
            
            return {
                "success": True, 
                "message": f"Dados convertidos e enviados com sucesso para {self.excel_path}",
                "projetos": len(projetos),
                "categorias": len(categorias),
                "logs": len(logs)
            }
            
        except Exception as e:
            logger.error(f"Erro ao converter JSON para Excel: {str(e)}")
            return {"success": False, "message": f"Erro: {str(e)}"}
    
    def excel_to_json(self):
        """
        Baixa o arquivo Excel do SharePoint e converte para arquivos JSON locais.
        
        Returns:
            dict: Resultado da operação com status e mensagem
        """
        try:
            if not self.sharepoint_client:
                return {"success": False, "message": "Cliente SharePoint não inicializado"}
            
            # Baixar o arquivo Excel do SharePoint
            excel_content = self.sharepoint_client.download_file(self.excel_path)
            
            # Ler as abas do Excel
            excel_file = io.BytesIO(excel_content)
            
            # Ler projetos
            df_projetos = pd.read_excel(excel_file, sheet_name='projetos')
            # Substituir valores NaN por None (que se torna null em JSON)
            df_projetos = df_projetos.replace({pd.NA: None})
            projetos = df_projetos.to_dict('records')
            
            # Resetar o ponteiro do arquivo
            excel_file.seek(0)
            
            # Ler categorias
            df_categorias = pd.read_excel(excel_file, sheet_name='categorias')
            # Substituir valores NaN por None (que se torna null em JSON)
            df_categorias = df_categorias.replace({pd.NA: None})
            categorias = df_categorias.to_dict('records')
            
            # Resetar o ponteiro do arquivo
            excel_file.seek(0)
            
            # Ler logs
            df_logs = pd.read_excel(excel_file, sheet_name='logs')
            # Substituir valores NaN por None (que se torna null em JSON)
            df_logs = df_logs.replace({pd.NA: None})
            logs = df_logs.to_dict('records')
            
            # Mesclar dados com os arquivos JSON existentes
            projetos_mesclados = self._merge_projects(projetos)
            categorias_mescladas = self._merge_categories(categorias)
            logs_mesclados = self._merge_logs(logs)
            
            # Salvar os arquivos JSON
            all_projetos_path = os.path.join(self.data_dir, 'all_projetos.json')
            categorias_path = os.path.join(self.data_dir, 'categorias.json')
            logs_path = os.path.join(self.data_dir, 'logs.json')
            
            with open(all_projetos_path, 'w', encoding='utf-8') as f:
                json.dump(projetos_mesclados, f, ensure_ascii=False, indent=2)
            
            with open(categorias_path, 'w', encoding='utf-8') as f:
                json.dump(categorias_mescladas, f, ensure_ascii=False, indent=2)
            
            with open(logs_path, 'w', encoding='utf-8') as f:
                json.dump(logs_mesclados, f, ensure_ascii=False, indent=2)
            
            # Registrar timestamp da sincronização
            self._save_sync_timestamp('download')
            
            return {
                "success": True, 
                "message": f"Dados baixados e convertidos com sucesso de {self.excel_path}",
                "projetos": len(projetos_mesclados),
                "categorias": len(categorias_mescladas),
                "logs": len(logs_mesclados)
            }
            
        except Exception as e:
            logger.error(f"Erro ao converter Excel para JSON: {str(e)}")
            return {"success": False, "message": f"Erro: {str(e)}"}
    
    def _merge_projects(self, new_projects):
        """
        Mescla projetos novos com os existentes, preservando categorizações.
        
        Args:
            new_projects: Lista de projetos do Excel
            
        Returns:
            list: Lista mesclada de projetos
        """
        try:
            # Campos de categorização que devem ser preservados
            campos_categorizacao = [
                '_aia_n1_macroarea',
                '_aia_n2_segmento',
                '_aia_n3_dominio_afeito',
                '_aia_n3_dominio_outro',
                'tecnologia_habilitadora',
                'area_aplicacao',
                'observacoes'
            ]
            
            # Carregar projetos existentes
            all_projetos_path = os.path.join(self.data_dir, 'all_projetos.json')
            if os.path.exists(all_projetos_path):
                with open(all_projetos_path, 'r', encoding='utf-8') as f:
                    existing_projects = json.load(f)
            else:
                existing_projects = []
            
            # Criar dicionário de projetos existentes para fácil acesso
            existing_dict = {str(p.get('codigo_projeto')): p for p in existing_projects}
            
            # Criar dicionário de projetos novos para fácil acesso
            new_dict = {str(p.get('codigo_projeto')): p for p in new_projects}
            
            # Lista para armazenar projetos mesclados
            merged_projects = []
            
            # Processar todos os projetos (existentes e novos)
            all_project_ids = set(list(existing_dict.keys()) + list(new_dict.keys()))
            
            for project_id in all_project_ids:
                if project_id in new_dict and project_id in existing_dict:
                    # Projeto existe em ambos, mesclar preservando categorização
                    merged_project = new_dict[project_id].copy()
                    
                    # Verificar se há campos de categorização preenchidos no projeto existente
                    for field in campos_categorizacao:
                        if field in existing_dict[project_id] and existing_dict[project_id].get(field):
                            # Verificar se o campo no novo projeto está vazio ou é diferente
                            if field not in merged_project or not merged_project.get(field):
                                merged_project[field] = existing_dict[project_id].get(field)
                            elif merged_project.get(field) != existing_dict[project_id].get(field):
                                # Se ambos têm valores diferentes, verificar qual é mais recente
                                # Aqui podemos usar a data de modificação ou outra lógica
                                # Por enquanto, vamos manter o valor do projeto existente
                                merged_project[field] = existing_dict[project_id].get(field)
                    
                    merged_projects.append(merged_project)
                elif project_id in new_dict:
                    # Projeto existe apenas nos novos
                    merged_projects.append(new_dict[project_id])
                else:
                    # Projeto existe apenas nos existentes
                    merged_projects.append(existing_dict[project_id])
            
            # Ordenar projetos por data_contrato (decrescente)
            merged_projects.sort(key=lambda x: x.get('data_contrato', ''), reverse=True)
            
            return merged_projects
            
        except Exception as e:
            logger.error(f"Erro ao mesclar projetos: {str(e)}")
            # Em caso de erro, retornar os novos projetos
            return new_projects
    
    def _merge_categories(self, new_categories):
        """
        Mescla categorias novas com as existentes.
        
        Args:
            new_categories: Lista de categorias do Excel
            
        Returns:
            list: Lista mesclada de categorias
        """
        try:
            # Carregar categorias existentes
            categorias_path = os.path.join(self.data_dir, 'categorias.json')
            if os.path.exists(categorias_path):
                with open(categorias_path, 'r', encoding='utf-8') as f:
                    existing_categories = json.load(f)
            else:
                existing_categories = []
            
            # Criar dicionário de categorias existentes para fácil acesso
            existing_dict = {str(c.get('id_projeto')): c for c in existing_categories}
            
            # Criar dicionário de categorias novas para fácil acesso
            new_dict = {str(c.get('id_projeto')): c for c in new_categories}
            
            # Lista para armazenar categorias mescladas
            merged_categories = []
            
            # Processar todas as categorias (existentes e novas)
            all_category_ids = set(list(existing_dict.keys()) + list(new_dict.keys()))
            
            for category_id in all_category_ids:
                if category_id in new_dict and category_id in existing_dict:
                    # Categoria existe em ambos, verificar qual é mais recente
                    # Por enquanto, vamos manter a categoria do Excel
                    merged_categories.append(new_dict[category_id])
                elif category_id in new_dict:
                    # Categoria existe apenas nas novas
                    merged_categories.append(new_dict[category_id])
                else:
                    # Categoria existe apenas nas existentes
                    merged_categories.append(existing_dict[category_id])
            
            return merged_categories
            
        except Exception as e:
            logger.error(f"Erro ao mesclar categorias: {str(e)}")
            # Em caso de erro, retornar as novas categorias
            return new_categories
    
    def _merge_logs(self, new_logs):
        """
        Mescla logs novos com os existentes.
        
        Args:
            new_logs: Lista de logs do Excel
            
        Returns:
            list: Lista mesclada de logs
        """
        try:
            # Carregar logs existentes
            logs_path = os.path.join(self.data_dir, 'logs.json')
            if os.path.exists(logs_path):
                with open(logs_path, 'r', encoding='utf-8') as f:
                    existing_logs = json.load(f)
            else:
                existing_logs = []
            
            # Criar dicionário de logs existentes para fácil acesso
            existing_dict = {str(l.get('id')): l for l in existing_logs}
            
            # Criar dicionário de logs novos para fácil acesso
            new_dict = {str(l.get('id')): l for l in new_logs}
            
            # Lista para armazenar logs mesclados
            merged_logs = []
            
            # Processar todos os logs (existentes e novos)
            all_log_ids = set(list(existing_dict.keys()) + list(new_dict.keys()))
            
            for log_id in all_log_ids:
                if log_id in new_dict and log_id in existing_dict:
                    # Log existe em ambos, verificar qual é mais recente
                    # Por enquanto, vamos manter o log do Excel
                    merged_logs.append(new_dict[log_id])
                elif log_id in new_dict:
                    # Log existe apenas nos novos
                    merged_logs.append(new_dict[log_id])
                else:
                    # Log existe apenas nos existentes
                    merged_logs.append(existing_dict[log_id])
            
            # Ordenar logs por ID (crescente)
            merged_logs.sort(key=lambda x: x.get('id', 0))
            
            return merged_logs
            
        except Exception as e:
            logger.error(f"Erro ao mesclar logs: {str(e)}")
            # Em caso de erro, retornar os novos logs
            return new_logs
    
    def _save_sync_timestamp(self, sync_type):
        """
        Salva o timestamp da última sincronização.
        
        Args:
            sync_type: Tipo de sincronização ('upload' ou 'download')
        """
        try:
            config_file = Config.CONFIG_FILE
            config = {}
            
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
            
            timestamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            
            if sync_type == 'upload':
                config['last_upload_sync'] = timestamp
            else:
                config['last_download_sync'] = timestamp
            
            with open(config_file, 'w') as f:
                json.dump(config, f)
                
        except Exception as e:
            logger.error(f"Erro ao salvar timestamp de sincronização: {str(e)}")
    
    def get_last_sync_timestamps(self):
        """
        Obtém os timestamps da última sincronização.
        
        Returns:
            dict: Timestamps de upload e download
        """
        try:
            config_file = Config.CONFIG_FILE
            
            if os.path.exists(config_file):
                with open(config_file, 'r') as f:
                    config = json.load(f)
                
                return {
                    'upload': config.get('last_upload_sync', 'Nunca'),
                    'download': config.get('last_download_sync', 'Nunca')
                }
            
            return {
                'upload': 'Nunca',
                'download': 'Nunca'
            }
                
        except Exception as e:
            logger.error(f"Erro ao obter timestamps de sincronização: {str(e)}")
            return {
                'upload': 'Erro',
                'download': 'Erro'
            }
