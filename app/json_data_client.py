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
            
            # Criar mapeamento de domínios por microárea e segmento
            dominios_por_microarea_segmento = {}
            for item in aia_data:
                microarea = item['Macroárea']
                segmento = item['Segmento']
                
                if 'Domínios Afeitos' in item:
                    if microarea not in dominios_por_microarea_segmento:
                        dominios_por_microarea_segmento[microarea] = {}
                    
                    if segmento not in dominios_por_microarea_segmento[microarea]:
                        dominios_por_microarea_segmento[microarea][segmento] = []
                    
                    domains = item['Domínios Afeitos'].split(';')
                    for domain in domains:
                        domain = domain.strip()
                        if domain and domain not in dominios_por_microarea_segmento[microarea][segmento]:
                            dominios_por_microarea_segmento[microarea][segmento].append(domain)
            
            # Extrair lista plana de todos os domínios para compatibilidade
            dominios = []
            for microarea_data in dominios_por_microarea_segmento.values():
                for segmento_dominios in microarea_data.values():
                    for dominio in segmento_dominios:
                        if dominio not in dominios:
                            dominios.append(dominio)
            
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
            
            # Adicionar o mapeamento de domínios por microárea e segmento
            result.append({
                'dominios_por_microarea_segmento': dominios_por_microarea_segmento
            })
            
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
            # Primeiro, verificar se há categorização no all_projetos.json
            project = self.get_project_by_id(None, project_id)
            
            if project and (project.get('_aia_n1_macroarea') or project.get('_aia_n2_segmento') or 
                           project.get('_aia_n3_dominio_afeito') or project.get('_aia_n3_dominio_outro')):
                # Obter domínios separadamente
                dominio_afeito = project.get('_aia_n3_dominio_afeito')
                dominio_outro = project.get('_aia_n3_dominio_outro')
                
                # Converter para o formato esperado pelo template
                return {
                    'id_projeto': project_id,
                    'microarea': project.get('_aia_n1_macroarea'),
                    'segmento': project.get('_aia_n2_segmento'),
                    'dominio': dominio_afeito,
                    'dominio_outros': dominio_outro,
                    'tecnologias_habilitadoras': project.get('tecnologia_habilitadora'),
                    'areas_aplicacao': project.get('area_aplicacao'),
                    'observacoes': project.get('observacoes')
                }
            
            # Se não encontrou no all_projetos.json, buscar no categorias.json (para compatibilidade)
            try:
                with open(os.path.join(self.data_dir, 'categorias.json'), 'r', encoding='utf-8') as f:
                    categories = json.load(f)
                
                # Buscar a categorização pelo código do projeto
                for category in categories:
                    if str(category.get('id_projeto')) == str(project_id):
                        return category
            except Exception as e:
                print(f"Aviso: Erro ao buscar categorização em categorias.json: {str(e)}")
            
            return None
            
        except Exception as e:
            raise Exception(f"Erro ao buscar categorização: {str(e)}")
    
    def get_ai_suggestions(self):
        """
        Obtém todas as sugestões da IA.
        
        Returns:
            list: Lista de dicionários com as sugestões da IA
        """
        try:
            suggestions_path = os.path.join(self.data_dir, 'ai_suggestions.json')
            if not os.path.exists(suggestions_path):
                with open(suggestions_path, 'w', encoding='utf-8') as f:
                    json.dump([], f, ensure_ascii=False, indent=2)
                return []
                
            with open(suggestions_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        except Exception as e:
            print(f"Erro ao ler sugestões da IA: {str(e)}")
            return []
    
    def get_ai_suggestion_by_project_id(self, project_id):
        """
        Obtém a sugestão da IA para um projeto específico.
        
        Args:
            project_id: ID ou código do projeto
            
        Returns:
            dict: Dados da sugestão da IA ou None se não encontrada
        """
        suggestions = self.get_ai_suggestions()
        for suggestion in suggestions:
            if str(suggestion.get('project_id')) == str(project_id):
                return suggestion
        return None
    
    def save_ai_suggestion(self, suggestion):
        """
        Salva uma sugestão da IA.
        
        Args:
            suggestion: Dicionário com a sugestão da IA
            
        Returns:
            bool: True se a operação for bem-sucedida
        """
        suggestions = self.get_ai_suggestions()
        
        # Verificar se já existe sugestão para este projeto
        for i, existing in enumerate(suggestions):
            if str(existing.get('project_id')) == str(suggestion.get('project_id')):
                # Atualizar sugestão existente
                suggestions[i] = suggestion
                break
        else:
            # Adicionar nova sugestão
            suggestions.append(suggestion)
        
        # Salvar no arquivo
        suggestions_path = os.path.join(self.data_dir, 'ai_suggestions.json')
        with open(suggestions_path, 'w', encoding='utf-8') as f:
            json.dump(suggestions, f, ensure_ascii=False, indent=2)
        
        return True
    
    def update_project_data(self, project_id, category_data):
        """
        Atualiza os dados de categorização diretamente no arquivo all_projetos.json
        
        Args:
            project_id: ID ou código do projeto a ser atualizado
            category_data: Dicionário com os dados de categorização
            
        Returns:
            bool: True se a atualização for bem-sucedida
        """
        try:
            # Carregar todos os projetos
            json_path = os.path.join(self.data_dir, 'all_projetos.json')
            with open(json_path, 'r', encoding='utf-8') as f:
                projects = json.load(f)
            
            # Buscar o projeto pelo código
            found = False
            for project in projects:
                if str(project.get('codigo_projeto')) == str(project_id):
                    # Atualizar os campos de categorização usando as chaves exatas do dicionário
                    # Isso permite que o método seja mais flexível quanto aos nomes dos campos
                    for key, value in category_data.items():
                        # Ignorar o campo id_projeto que é apenas para referência
                        # E também ignorar o campo validation_info
                        if key != 'id_projeto' and key != 'validation_info':
                            project[key] = value
                    
                    found = True
                    break
            
            if not found:
                return False
            
            # Salvar dados atualizados
            with open(json_path, 'w', encoding='utf-8') as f:
                json.dump(projects, f, ensure_ascii=False, indent=2)
            
            return True
            
        except Exception as e:
            raise Exception(f"Erro ao atualizar dados do projeto: {str(e)}")
