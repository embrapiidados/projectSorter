import json
import os
from datetime import datetime
import copy

class JsonDataClient:
    """
    Cliente para manipulação de dados em arquivos JSON locais.
    Substitui o SharePointClient para operações de dados.
    """
    
    def __init__(self):
        """Inicializa o cliente de dados JSON."""
        self.data_dir = 'app/data'
        
        # Garantir que os arquivos necessários existam
        self._ensure_files_exist()
    
    def _ensure_files_exist(self):
        """Garante que todos os arquivos JSON necessários existam."""
        # Verificar e criar categorias.json se não existir
        categorias_path = os.path.join(self.data_dir, 'categorias.json')
        if not os.path.exists(categorias_path):
            with open(categorias_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
        
        # Verificar e criar logs.json se não existir
        logs_path = os.path.join(self.data_dir, 'logs.json')
        if not os.path.exists(logs_path):
            with open(logs_path, 'w', encoding='utf-8') as f:
                json.dump([], f, ensure_ascii=False, indent=2)
    
    def get_excel_data(self, file_path, sheet_name):
        """
        Emula o comportamento do método get_excel_data do SharePointClient,
        mas usando arquivos JSON locais.
        
        Args:
            file_path: Ignorado, mantido para compatibilidade
            sheet_name: Nome da "aba" (tipo de dados) a ser carregada
            
        Returns:
            list: Lista de dicionários com os dados solicitados
        """
        try:
            if sheet_name == 'projetos':
                # Carregar dados de projetos do all_projetos.json
                with open(os.path.join(self.data_dir, 'all_projetos.json'), 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            elif sheet_name == 'categorias':
                # Carregar dados de categorias do categorias.json
                with open(os.path.join(self.data_dir, 'categorias.json'), 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            elif sheet_name == 'logs':
                # Carregar dados de logs do logs.json
                with open(os.path.join(self.data_dir, 'logs.json'), 'r', encoding='utf-8') as f:
                    return json.load(f)
            
            elif sheet_name == 'categorias_lists':
                # Gerar listas de categorias a partir do aia.json
                return self.get_categories_lists()
            
            else:
                raise ValueError(f"Tipo de dados desconhecido: {sheet_name}")
                
        except Exception as e:
            raise Exception(f"Erro ao ler dados JSON: {str(e)}")
    
    def get_categories_lists(self):
        """
        Obtém as listas de categorias a partir do arquivo aia.json.
        
        Returns:
            list: Lista de dicionários com as opções de categorias
        """
        try:
            # Carregar dados do aia.json
            with open(os.path.join(self.data_dir, 'aia.json'), 'r', encoding='utf-8') as f:
                aia_data = json.load(f)
            
            # Extrair valores únicos para cada categoria
            microareas = list(set(item['Macroárea'] for item in aia_data))
            segmentos = list(set(item['Segmento'] for item in aia_data))
            
            # Extrair domínios dos "Domínios Afeitos"
            dominios = []
            for item in aia_data:
                if 'Domínios Afeitos' in item:
                    domains = item['Domínios Afeitos'].split(';')
                    for domain in domains:
                        domain = domain.strip()
                        if domain and domain not in dominios:
                            dominios.append(domain)
            
            # Criar lista de dicionários no formato esperado pelo sistema
            result = []
            
            # Determinar o tamanho máximo das listas
            max_length = max(len(microareas), len(segmentos), len(dominios))
            
            # Preencher com valores vazios para tecnologias_habilitadoras e areas_aplicacao
            # (estas categorias não estão no aia.json)
            tecnologias = ["Inteligência Artificial", "Internet das Coisas", "Blockchain", 
                          "Computação em Nuvem", "Big Data", "Robótica", "Biotecnologia"]
            areas = ["Saúde", "Agricultura", "Indústria", "Energia", "Transporte", 
                    "Finanças", "Educação", "Segurança"]
            
            # Criar a lista de dicionários
            for i in range(max_length):
                item = {}
                
                # Adicionar microarea se disponível
                if i < len(microareas):
                    item['microarea'] = microareas[i]
                else:
                    item['microarea'] = None
                
                # Adicionar segmento se disponível
                if i < len(segmentos):
                    item['segmento'] = segmentos[i]
                else:
                    item['segmento'] = None
                
                # Adicionar dominio se disponível
                if i < len(dominios):
                    item['dominio'] = dominios[i]
                else:
                    item['dominio'] = None
                
                # Adicionar tecnologia habilitadora se disponível
                if i < len(tecnologias):
                    item['tecnologias_habilitadoras'] = tecnologias[i]
                else:
                    item['tecnologias_habilitadoras'] = None
                
                # Adicionar área de aplicação se disponível
                if i < len(areas):
                    item['areas_aplicacao'] = areas[i]
                else:
                    item['areas_aplicacao'] = None
                
                result.append(item)
            
            return result
            
        except Exception as e:
            raise Exception(f"Erro ao gerar listas de categorias: {str(e)}")
    
    def update_excel_data(self, file_path, sheet_name, data, id_column=None):
        """
        Emula o comportamento do método update_excel_data do SharePointClient,
        mas salvando em arquivos JSON locais.
        
        Args:
            file_path: Ignorado, mantido para compatibilidade
            sheet_name: Nome da "aba" (tipo de dados) a ser atualizada
            data: Dados para atualização (dict para registro único, list para múltiplos)
            id_column: Nome da coluna de ID para atualização de registro específico
            
        Returns:
            bool: True se a atualização for bem-sucedida
        """
        try:
            if sheet_name == 'categorias':
                # Atualizar dados de categorias no categorias.json
                json_path = os.path.join(self.data_dir, 'categorias.json')
                
                # Carregar dados existentes
                with open(json_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                
                if isinstance(data, dict) and id_column is not None:
                    # Atualizar um registro específico
                    found = False
                    for i, item in enumerate(existing_data):
                        if str(item.get(id_column)) == str(data.get(id_column)):
                            existing_data[i] = data
                            found = True
                            break
                    
                    # Se não encontrou, adicionar novo registro
                    if not found:
                        existing_data.append(data)
                
                elif isinstance(data, list):
                    # Substituir todos os dados
                    existing_data = data
                
                # Salvar dados atualizados
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
            elif sheet_name == 'logs':
                # Atualizar dados de logs no logs.json
                json_path = os.path.join(self.data_dir, 'logs.json')
                
                # Carregar dados existentes
                with open(json_path, 'r', encoding='utf-8') as f:
                    existing_data = json.load(f)
                
                if isinstance(data, list):
                    # Substituir ou adicionar dados
                    existing_data = data
                else:
                    # Adicionar um único registro
                    existing_data.append(data)
                
                # Salvar dados atualizados
                with open(json_path, 'w', encoding='utf-8') as f:
                    json.dump(existing_data, f, ensure_ascii=False, indent=2)
            
            elif sheet_name == 'categorias_lists':
                # Esta operação não é suportada diretamente, pois as listas são geradas do aia.json
                # Poderia ser implementada se necessário
                pass
            
            else:
                raise ValueError(f"Tipo de dados desconhecido para atualização: {sheet_name}")
            
            return True
            
        except Exception as e:
            raise Exception(f"Erro ao atualizar dados JSON: {str(e)}")
    
    def get_project_by_id(self, excel_path, project_id):
        """
        Obtém um projeto específico pelo ID.
        
        Args:
            excel_path: Ignorado, mantido para compatibilidade
            project_id: ID ou código do projeto a ser buscado
            
        Returns:
            dict: Dados do projeto ou None se não encontrado
        """
        try:
            # Carregar todos os projetos
            with open(os.path.join(self.data_dir, 'all_projetos.json'), 'r', encoding='utf-8') as f:
                projects = json.load(f)
            
            # Buscar o projeto pelo código do projeto
            for project in projects:
                if str(project.get('codigo_projeto')) == str(project_id):
                    return project
            
            return None
            
        except Exception as e:
            raise Exception(f"Erro ao buscar projeto: {str(e)}")
    
    def get_categorization_by_project_id(self, excel_path, project_id):
        """
        Obtém a categorização de um projeto pelo ID.
        
        Args:
            excel_path: Ignorado, mantido para compatibilidade
            project_id: ID ou código do projeto
            
        Returns:
            dict: Dados da categorização ou None se não encontrada
        """
        try:
            # Carregar todas as categorizações
            with open(os.path.join(self.data_dir, 'categorias.json'), 'r', encoding='utf-8') as f:
                categories = json.load(f)
            
            # Buscar a categorização pelo código do projeto
            for category in categories:
                if str(category.get('id_projeto')) == str(project_id):
                    return category
            
            return None
            
        except Exception as e:
            raise Exception(f"Erro ao buscar categorização: {str(e)}")
