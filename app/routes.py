from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from app.json_data_client import JsonDataClient
from app.excel_manager import ExcelManager
from app.ai_integration import OpenAIClient
from app.sync_manager import SyncManager
from config import Config
import json
import os
from datetime import datetime

main = Blueprint('main', __name__)

# Middleware para verificar autenticação
@main.before_request
def check_auth():
    # Como não estamos mais usando SharePoint, podemos simplificar a autenticação
    # ou removê-la completamente se não for mais necessária
    pass

# Rota para a página inicial
@main.route('/')
def index():
    return redirect(url_for('main.projects'))

# Rota para login
@main.route('/login', methods=['GET', 'POST'])
def login():
    # Como estamos usando JSON local, não precisamos mais de autenticação no SharePoint
    # Podemos redirecionar diretamente para a página de projetos
    return redirect(url_for('main.projects'))

# Rota para listagem de projetos
@main.route('/projects')
def projects():
    try:
        # Usar o novo cliente JSON
        json_client = JsonDataClient()
        
        # Obter dados dos projetos
        projects_data = json_client.get_excel_data(
            None,  # Não precisamos mais do caminho do Excel
            'projetos'
        )
        
        # Obter dados de categorização
        try:
            categorias_data = json_client.get_excel_data(None, 'categorias')
        except Exception as e:
            print(f"Aviso: Erro ao carregar categorias: {str(e)}")
            categorias_data = []
        
        # Criar um conjunto de IDs de projetos categorizados para busca rápida
        categorized_project_ids = set()
        for categoria in categorias_data:
            project_id = categoria.get('id_projeto')
            if project_id:
                categorized_project_ids.add(project_id)
        
        # Adicionar informação de categorização a cada projeto
        for project in projects_data:
            project_id = project.get('codigo_projeto')
            project['categorizado'] = project_id in categorized_project_ids
        
        # Ordenar projetos: não categorizados primeiro, depois categorizados
        projects_data = sorted(projects_data, key=lambda x: x.get('categorizado', False))
        
        return render_template('projects.html', projects=projects_data)
        
    except Exception as e:
        flash(f'Erro ao carregar projetos: {str(e)}', 'error')
        return redirect(url_for('main.login'))

# Função para registrar log de categorização
def log_categorization(project_id, used_ai=False, validation_info=None, user_modified=False):
    try:
        json_client = JsonDataClient()
        
        # Obter logs existentes para determinar próximo ID
        try:
            logs = json_client.get_excel_data(
                None,
                'logs'
            )
            # Determinar o próximo ID
            next_id = 1
            if logs and len(logs) > 0:
                ids = [log.get('id', 0) for log in logs]
                next_id = max(ids) + 1
        except Exception as e:
            # Se o arquivo não existir ou ocorrer erro, começar do ID 1
            print(f"Aviso: Não foi possível ler logs existentes: {str(e)}")
            logs = []
            next_id = 1
        
        # Criar registro de log
        log_data = {
            'id': next_id,
            'id_projeto': project_id,
            'email': session.get('sharepoint_username', 'sistema'),
            'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ia': 'Sim' if used_ai else 'Não',
            'user_modified': user_modified
        }
        
        # Adicionar informações de validação se disponíveis
        if validation_info:
            log_data['validation_info'] = validation_info
        
        # Adicionar o log ao arquivo JSON
        if logs:
            # Adicionar ao final da lista existente
            logs.append(log_data)
            json_client.update_excel_data(
                None,
                'logs',
                logs
            )
        else:
            # Criar lista com apenas este log
            json_client.update_excel_data(
                None,
                'logs',
                [log_data]
            )
        
        print(f"Log de categorização registrado: {log_data}")
        return True
    except Exception as e:
        print(f"Erro ao registrar log de categorização: {str(e)}")
        return False

# Função para extrair nome do email
def extract_name_from_email(email):
    """
    Extrai o nome do usuário a partir do email.
    Exemplo: lucas.pinheiro@embrapii.org.br -> Lucas Pinheiro
    """
    try:
        # Remove o domínio
        username = email.split('@')[0]
        # Substitui pontos por espaços
        name_parts = username.replace('.', ' ').split()
        # Capitaliza cada parte
        capitalized_parts = [part.capitalize() for part in name_parts]
        # Junta as partes
        return ' '.join(capitalized_parts)
    except:
        return email  # Retorna o email original em caso de erro

# Função para obter logs de um projeto específico
def get_project_logs(project_id):
    """
    Obtém os logs de categorização para um projeto específico.
    """
    try:
        json_client = JsonDataClient()
        all_logs = json_client.get_excel_data(None, 'logs')
        
        # Filtrar logs pelo ID do projeto
        project_logs = [log for log in all_logs if str(log.get('id_projeto')) == str(project_id)]
        
        # Adicionar nome formatado para cada log
        for log in project_logs:
            if 'email' in log:
                log['nome_usuario'] = extract_name_from_email(log['email'])
        
        return project_logs
    except Exception as e:
        print(f"Erro ao obter logs do projeto: {str(e)}")
        return []

# Rota para categorização de um projeto
@main.route('/categorize/<project_id>', methods=['GET', 'POST'])
@main.route('/categorize/<project_id>/', methods=['GET', 'POST'])
def categorize(project_id):
    try:
        json_client = JsonDataClient()
        
        if request.method == 'POST':
            # Processar o formulário de categorização
            # Obter múltiplos domínios selecionados
            dominio_values = request.form.getlist('dominio')
            dominio_str = ';'.join(dominio_values) if dominio_values else None
            
            # Obter múltiplos domínios outros selecionados
            dominio_outros_values = request.form.getlist('dominio_outros')
            dominio_outros_str = ';'.join(dominio_outros_values) if dominio_outros_values else None
            
            category_data = {
                'id_projeto': project_id,  # Agora usando codigo_projeto como identificador
                '_aia_n1_macroarea': request.form.get('microarea'),
                '_aia_n2_segmento': request.form.get('segmento'),
                '_aia_n3_dominio_afeito': dominio_str,
                '_aia_n3_dominio_outro': dominio_outros_str,
                'observacoes': request.form.get('observacoes')
            }
            
            # Verificar se utilizou a IA (através de um campo oculto no form)
            used_ai = request.form.get('used_ai') == 'true'
            
            # Verificar se o usuário modificou os campos (através de um campo oculto no form)
            user_modified = request.form.get('user_modified') == 'true'
            
            # Atualizar diretamente no all_projetos.json
            if json_client.update_project_data(project_id, category_data):
                # Continuar salvando em categorias.json para compatibilidade
                json_client.update_excel_data(
                    None,
                    'categorias',
                    category_data,
                    'id_projeto'
                )
                
                # Registrar log da categorização
                log_categorization(project_id, used_ai, None, user_modified)
                
                flash('Categorização salva com sucesso!', 'success')
            else:
                flash('Erro: Projeto não encontrado para atualização', 'error')
                
            return redirect(url_for('main.projects'))
        
        # Obter dados do projeto
        project = json_client.get_project_by_id(
            None,
            project_id
        )
        
        if not project:
            flash('Projeto não encontrado', 'error')
            return redirect(url_for('main.projects'))
        
        # Verificar se já existe uma categorização manual para este projeto
        existing = json_client.get_categorization_by_project_id(None, project_id)
        
        # Verificar se já existe uma sugestão da IA para este projeto
        existing_suggestion = json_client.get_ai_suggestion_by_project_id(project_id)
        
        # Inicializar variável para a sugestão da IA
        ai_suggestion = None
        
        # Verificar se devemos gerar uma nova sugestão da IA
        should_generate_new_suggestion = True
        
        # Não gerar nova sugestão se já existir categorização manual
        if existing and (existing.get('microarea') or existing.get('segmento') or 
                        existing.get('dominio') or existing.get('dominio_outros')):
            should_generate_new_suggestion = False
            print(f"Categorização manual existente para o projeto {project_id}. Não gerando nova sugestão da IA.")
        
        # Não gerar nova sugestão se já existir uma sugestão com confiança ALTA
        elif existing_suggestion and existing_suggestion.get('confianca') == 'ALTA':
            should_generate_new_suggestion = False
            ai_suggestion = existing_suggestion
            # Adicionar flag para indicar que estamos reutilizando uma sugestão existente
            ai_suggestion['is_reused_suggestion'] = True
            print(f"Sugestão da IA com confiança ALTA já existe para o projeto {project_id}. Usando sugestão existente.")
        
        # Gerar nova sugestão da IA se necessário
        openai_api_key = Config.get_openai_api_key()
        
        if should_generate_new_suggestion and openai_api_key:
            try:
                # Obter dados do aia.json
                with open('app/data/aia.json', 'r', encoding='utf-8') as f:
                    aia_data = json.load(f)
                
                # Chamar OpenAI para sugerir categorias
                openai_client = OpenAIClient(openai_api_key)
                suggestion = openai_client.suggest_categories(project, None, aia_data)
                
                # Adicionar ID do projeto e flag para indicar que é uma sugestão da IA
                suggestion['project_id'] = project_id
                suggestion['is_ai_suggestion'] = True
                
                # Garantir que todos os campos tenham vírgulas entre eles e tratar o campo dominio_outro
                for key in suggestion:
                    if isinstance(suggestion[key], str):
                        suggestion[key] = suggestion[key].strip()
                
                # Verificar se o campo _aia_n3_dominio_outro está vazio ou é N/A
                if '_aia_n3_dominio_outro' in suggestion:
                    dominio_outro = suggestion['_aia_n3_dominio_outro'].strip()
                    if dominio_outro == '' or dominio_outro.lower() == 'n/a':
                        suggestion['_aia_n3_dominio_outro'] = 'N/A'
                
                # Salvar sugestão
                json_client.save_ai_suggestion(suggestion)
                
                # Atualizar a variável ai_suggestion
                ai_suggestion = suggestion
                
                # Armazenar a sugestão na sessão para uso posterior
                session['ai_suggestion'] = suggestion
                
                print(f"Sugestão da IA gerada com sucesso: {ai_suggestion}")
            except Exception as e:
                print(f"Erro ao obter sugestão da IA: {str(e)}")
        elif existing_suggestion and not ai_suggestion:
            # Se não geramos uma nova sugestão, mas existe uma sugestão anterior (não ALTA),
            # usar a sugestão existente
            ai_suggestion = existing_suggestion
            # Adicionar flag para indicar que estamos reutilizando uma sugestão existente
            ai_suggestion['is_reused_suggestion'] = True
            session['ai_suggestion'] = existing_suggestion
            print(f"Usando sugestão da IA existente para o projeto {project_id}.")
        
        # Obter listas de categorias
        categories_lists = json_client.get_excel_data(
            None,
            'categorias_lists'
        )
        
        # Organizar as listas por tipo
        organized_lists = {}
        for column in ['tecnologias_habilitadoras', 'areas_aplicacao', 'microarea', 'segmento', 'dominio']:
            organized_lists[column] = list(set([item.get(column, '') for item in categories_lists if item.get(column)]))
        
        # Obter o mapeamento de domínios por microárea e segmento
        dominios_por_microarea_segmento = None
        for item in categories_lists:
            if isinstance(item, dict) and 'dominios_por_microarea_segmento' in item:
                dominios_por_microarea_segmento = item['dominios_por_microarea_segmento']
                break
        
        # Adicionar o mapeamento às listas organizadas como string JSON
        if dominios_por_microarea_segmento:
            organized_lists['dominios_por_microarea_segmento_json'] = json.dumps(dominios_por_microarea_segmento)
        
        # Obter categorização existente
        existing = json_client.get_categorization_by_project_id(
            None,
            project_id
        )
        
        # Log para depuração
        print(f"Categorização existente para o projeto {project_id}:", existing)
        
        # Obter logs do projeto
        project_logs = get_project_logs(project_id)
        
        # Verificar se a chave da OpenAI está configurada
        openai_api_key = Config.get_openai_api_key()
        
        # Garantir que os valores existentes sejam strings para evitar problemas no template
        if existing:
            for key in ['microarea', 'segmento', 'dominio', 'dominio_outros']:
                if key in existing and existing[key] is None:
                    existing[key] = ''
        
        return render_template(
            'categorize.html',
            project=project,
            categories_lists=organized_lists,
            existing=existing,
            ai_suggestion=ai_suggestion,  # Passar a sugestão da IA para o template
            openai_enabled=(openai_api_key != ''),
            project_logs=project_logs  # Passar os logs do projeto para o template
        )
        
    except Exception as e:
        flash(f'Erro: {str(e)}', 'error')
        return redirect(url_for('main.projects'))

# Rota para gerenciar listas de categorias
@main.route('/lists', methods=['GET', 'POST'])
def lists():
    try:
        json_client = JsonDataClient()
        
        if request.method == 'POST':
            # Processar o formulário de atualização de listas
            lists_data = {}
            
            for column in ['tecnologias_habilitadoras', 'areas_aplicacao', 'microarea', 'segmento', 'dominio']:
                values = request.form.getlist(f'{column}[]')
                # Filtrar valores vazios
                values = [v for v in values if v.strip()]
                lists_data[column] = values
            
            # Converter para o formato esperado
            excel_data = []
            max_length = max(len(values) for values in lists_data.values())
            
            for i in range(max_length):
                row = {}
                for column, values in lists_data.items():
                    row[column] = values[i] if i < len(values) else None
                excel_data.append(row)
            
            # Atualizar no JSON
            # Nota: Esta operação pode não ser suportada diretamente pelo JsonDataClient
            # pois as listas são geradas a partir do aia.json
            flash('Funcionalidade não suportada com JSON local', 'warning')
            return redirect(url_for('main.lists'))
        
        # Obter listas de categorias
        categories_lists = json_client.get_excel_data(
            None,
            'categorias_lists'
        )
        
        # Organizar as listas por tipo
        organized_lists = {}
        for column in ['tecnologias_habilitadoras', 'areas_aplicacao', 'microarea', 'segmento', 'dominio']:
            organized_lists[column] = list(set([item.get(column, '') for item in categories_lists if item.get(column)]))
        
        return render_template('lists.html', categories_lists=organized_lists)
        
    except Exception as e:
        flash(f'Erro: {str(e)}', 'error')
        return redirect(url_for('main.projects'))

# Rota para visualização de logs
@main.route('/logs')
def view_logs():
    try:
        json_client = JsonDataClient()
        
        # Obter logs
        try:
            logs = json_client.get_excel_data(
                None,
                'logs'
            )
        except Exception as e:
            print(f"Erro ao obter logs: {str(e)}")
            logs = []
        
        # Obter projetos para exibir nomes em vez de IDs
        projects = json_client.get_excel_data(
            None,
            'projetos'
        )
        
        # Criar mapeamento de ID para título do projeto
        project_names = {}
        for project in projects:
            project_names[str(project.get('id'))] = project.get('titulo', 'Projeto sem título')
        
        # Adicionar título do projeto aos logs
        for log in logs:
            project_id = str(log.get('id_projeto'))
            log['projeto_titulo'] = project_names.get(project_id, f"Projeto {project_id}")
        
        return render_template('logs.html', logs=logs)
        
    except Exception as e:
        flash(f'Erro ao carregar logs: {str(e)}', 'error')
        return redirect(url_for('main.projects'))

# Rota para configurações
@main.route('/settings', methods=['GET', 'POST'])
def settings():
    if request.method == 'POST':
        openai_api_key = request.form.get('openai_api_key', '')
        
        # Salvar chave da API
        if Config.save_openai_api_key(openai_api_key):
            flash('Configurações salvas com sucesso!', 'success')
        else:
            flash('Erro ao salvar configurações', 'error')
        
        return redirect(url_for('main.settings'))
    
    # Obter chave atual
    openai_api_key = Config.get_openai_api_key()
    
    return render_template('settings.html', openai_api_key=openai_api_key)

# Rota para sugestão automática de categorias
@main.route('/api/suggest-categories', methods=['POST'])
def suggest_categories():
    try:
        data = request.json
        project_id = data.get('project_id')
        
        if not project_id:
            return jsonify({'error': 'ID do projeto não fornecido'}), 400
        
        # Obter chave da API do OpenAI
        openai_api_key = Config.get_openai_api_key()
        
        if not openai_api_key:
            return jsonify({'error': 'Chave da API OpenAI não configurada'}), 400
        
        # Usar o cliente JSON
        json_client = JsonDataClient()
        
        # Obter dados do projeto
        project = json_client.get_project_by_id(
            None,
            project_id
        )
        
        if not project:
            return jsonify({'error': 'Projeto não encontrado'}), 404
        
        # Obter listas de categorias
        categories_lists_data = json_client.get_excel_data(
            None,
            'categorias_lists'
        )
        
        # Organizar as listas por tipo
        organized_lists = {}
        for column in ['tecnologias_habilitadoras', 'areas_aplicacao', 'microarea', 'segmento', 'dominio']:
            organized_lists[column] = list(set([item.get(column, '') for item in categories_lists_data if item.get(column)]))
        
        # Obter dados do aia.json
        try:
            with open('app/data/aia.json', 'r', encoding='utf-8') as f:
                aia_data = json.load(f)
        except Exception as e:
            print(f"Aviso: Não foi possível carregar aia.json: {str(e)}")
            aia_data = None
        
        # Chamar OpenAI para sugerir categorias
        openai_client = OpenAIClient(openai_api_key)
        suggestions = openai_client.suggest_categories(project, organized_lists, aia_data)
        
        # Verificar se há múltiplos domínios sugeridos e formatá-los corretamente
        if 'dominio' in suggestions and isinstance(suggestions['dominio'], list):
            suggestions['dominio'] = ';'.join(suggestions['dominio'])
        
        # Armazenar a sugestão na sessão para uso posterior
        session['ai_suggestion'] = suggestions
        
        return jsonify(suggestions)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para validação de sugestões da IA
@main.route('/api/validate-suggestion', methods=['POST'])
def validate_suggestion():
    try:
        data = request.json
        project_id = data.get('project_id')
        validation = data.get('validation', {})
        
        # Adicionar campos manuais ao objeto de validação
        for field in ['microarea', 'segmento', 'dominio']:
            manual_field = f'manual_{field}'
            if manual_field in data:
                validation[manual_field] = data.get(manual_field)
        
        # Tratar especificamente o campo dominio_outros/dominio_outro
        if 'manual_dominio_outros' in data:
            validation['manual_dominio_outros'] = data.get('manual_dominio_outros')
            # Também adicionar como manual_dominio_outro para compatibilidade
            validation['manual_dominio_outro'] = data.get('manual_dominio_outros')
        
        if not project_id:
            return jsonify({'error': 'ID do projeto não fornecido'}), 400
        
        # Obter a sugestão da IA da sessão
        suggestion = session.get('ai_suggestion')
        
        if not suggestion:
            return jsonify({'error': 'Nenhuma sugestão da IA encontrada na sessão'}), 400
        
        # Obter chave da API do OpenAI para processar a validação
        openai_api_key = Config.get_openai_api_key()
        
        if not openai_api_key:
            return jsonify({'error': 'Chave da API OpenAI não configurada'}), 400
        
        # Processar a validação
        openai_client = OpenAIClient(openai_api_key)
        result = openai_client.process_validation(suggestion, validation)
        
        # Usar o cliente JSON
        json_client = JsonDataClient()
        
        # Preparar dados para salvar - usar diretamente o resultado do process_validation
        # que agora já contém as chaves corretas (_aia_n1_macroarea, etc.)
        category_data = {
            'id_projeto': project_id,
            '_aia_n1_macroarea': result.get('_aia_n1_macroarea', ''),
            '_aia_n2_segmento': result.get('_aia_n2_segmento', ''),
            '_aia_n3_dominio_afeito': result.get('_aia_n3_dominio_afeito', ''),
            '_aia_n3_dominio_outro': result.get('_aia_n3_dominio_outro', '')
            # Removido o campo validation_info
        }
        
        # Adicionar logs para depuração
        print(f"Dados a serem salvos: {category_data}")
        
        # Atualizar no all_projetos.json
        if json_client.update_project_data(project_id, category_data):
            # Continuar salvando em categorias.json para compatibilidade
            # Converter para o formato esperado pelo categorias.json
            categorias_data = {
                'id_projeto': project_id,
                'microarea': result.get('_aia_n1_macroarea', ''),
                'segmento': result.get('_aia_n2_segmento', ''),
                'dominio': result.get('_aia_n3_dominio_afeito', ''),
                'dominio_outros': result.get('_aia_n3_dominio_outro', '')
                # Removido o campo validation_info
            }
            
            json_client.update_excel_data(
                None,
                'categorias',
                categorias_data,
                'id_projeto'
            )
            
            # Registrar log da categorização
            # Neste caso, consideramos que o usuário modificou os campos se houver campos manuais no objeto de validação
            user_modified = any(key.startswith('manual_') for key in validation.keys())
            log_categorization(project_id, True, validation, user_modified)
            
            return jsonify({'success': True, 'message': 'Validação processada com sucesso'})
        else:
            return jsonify({'error': 'Erro ao atualizar dados do projeto'}), 500
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para lidar com /categorize/ sem project_id
@main.route('/categorize/', methods=['GET'])
def categorize_no_id():
    flash('É necessário selecionar um projeto para categorizar', 'warning')
    return redirect(url_for('main.projects'))

# Rota para sincronização
@main.route('/sync', methods=['GET'])
def sync():
    try:
        # Criar gerenciador de sincronização
        sync_manager = SyncManager()
        
        # Verificar se há credenciais do SharePoint na sessão ou no .env
        sharepoint_connected = False
        
        # Primeiro tentar com as credenciais da sessão
        if all(key in session for key in ['sharepoint_username', 'sharepoint_password', 'sharepoint_site_url']):
            try:
                # Tentar conectar ao SharePoint com credenciais da sessão
                sharepoint_connected = sync_manager.connect_sharepoint(
                    session['sharepoint_username'],
                    session['sharepoint_password'],
                    session['sharepoint_site_url']
                )
            except Exception as e:
                print(f"Erro ao conectar ao SharePoint com credenciais da sessão: {str(e)}")
        
        # Se não conectou com as credenciais da sessão, tentar com as do .env
        if not sharepoint_connected:
            try:
                # Tentar conectar ao SharePoint com credenciais do .env
                sharepoint_connected = sync_manager.connect_sharepoint()
                if sharepoint_connected:
                    # Se conectou com sucesso, salvar as credenciais na sessão
                    session['sharepoint_username'] = os.environ.get('sharepoint_email')
                    session['sharepoint_password'] = os.environ.get('sharepoint_password')
                    session['sharepoint_site_url'] = os.environ.get('sharepoint_url_site')
            except Exception as e:
                print(f"Erro ao conectar ao SharePoint com credenciais do .env: {str(e)}")
        
        # Obter timestamps de sincronização
        timestamps = sync_manager.get_last_sync_timestamps()
        
        # Verificar se a sincronização automática está habilitada
        config_file = Config.CONFIG_FILE
        auto_sync = False
        if os.path.exists(config_file):
            try:
                with open(config_file, 'r') as f:
                    config = json.load(f)
                    auto_sync = config.get('auto_sync', False)
            except Exception as e:
                print(f"Erro ao ler configuração: {str(e)}")
        
        return render_template(
            'sync.html',
            timestamps=timestamps,
            excel_path=Config.SHAREPOINT_EXCEL_PATH,
            sharepoint_connected=sharepoint_connected,
            auto_sync=auto_sync
        )
        
    except Exception as e:
        flash(f'Erro: {str(e)}', 'error')
        return redirect(url_for('main.projects'))

# Rota para upload de JSON para Excel no SharePoint
@main.route('/sync/upload', methods=['POST'])
def sync_upload():
    try:
        # Obter credenciais do formulário, da sessão ou do .env
        username = request.form.get('username') or session.get('sharepoint_username') or os.environ.get('sharepoint_email')
        password = request.form.get('password') or session.get('sharepoint_password') or os.environ.get('sharepoint_password')
        site_url = request.form.get('site_url') or session.get('sharepoint_site_url') or os.environ.get('sharepoint_url_site')
        
        if not all([username, password, site_url]):
            flash('Credenciais do SharePoint incompletas', 'error')
            return redirect(url_for('main.sync'))
        
        # Salvar credenciais na sessão
        session['sharepoint_username'] = username
        session['sharepoint_password'] = password
        session['sharepoint_site_url'] = site_url
        
        # Criar gerenciador de sincronização
        sync_manager = SyncManager()
        
        # Conectar ao SharePoint
        if not sync_manager.connect_sharepoint(username, password, site_url):
            flash('Erro ao conectar ao SharePoint', 'error')
            return redirect(url_for('main.sync'))
        
        # Converter JSON para Excel e fazer upload
        result = sync_manager.json_to_excel()
        
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'error')
        
        return render_template(
            'sync.html',
            timestamps=sync_manager.get_last_sync_timestamps(),
            excel_path=Config.SHAREPOINT_EXCEL_PATH,
            sharepoint_connected=True,
            result=result,
            auto_sync=Config.get_auto_sync()
        )
        
    except Exception as e:
        flash(f'Erro: {str(e)}', 'error')
        return redirect(url_for('main.sync'))

# Rota para download de Excel do SharePoint para JSON
@main.route('/sync/download', methods=['POST'])
def sync_download():
    try:
        # Obter credenciais do formulário, da sessão ou do .env
        username = request.form.get('username') or session.get('sharepoint_username') or os.environ.get('sharepoint_email')
        password = request.form.get('password') or session.get('sharepoint_password') or os.environ.get('sharepoint_password')
        site_url = request.form.get('site_url') or session.get('sharepoint_site_url') or os.environ.get('sharepoint_url_site')
        
        if not all([username, password, site_url]):
            flash('Credenciais do SharePoint incompletas', 'error')
            return redirect(url_for('main.sync'))
        
        # Salvar credenciais na sessão
        session['sharepoint_username'] = username
        session['sharepoint_password'] = password
        session['sharepoint_site_url'] = site_url
        
        # Criar gerenciador de sincronização
        sync_manager = SyncManager()
        
        # Conectar ao SharePoint
        if not sync_manager.connect_sharepoint(username, password, site_url):
            flash('Erro ao conectar ao SharePoint', 'error')
            return redirect(url_for('main.sync'))
        
        # Baixar Excel e converter para JSON
        result = sync_manager.excel_to_json()
        
        if result['success']:
            flash(result['message'], 'success')
        else:
            flash(result['message'], 'error')
        
        return render_template(
            'sync.html',
            timestamps=sync_manager.get_last_sync_timestamps(),
            excel_path=Config.SHAREPOINT_EXCEL_PATH,
            sharepoint_connected=True,
            result=result,
            auto_sync=Config.get_auto_sync()
        )
        
    except Exception as e:
        flash(f'Erro: {str(e)}', 'error')
        return redirect(url_for('main.sync'))

# Rota para alternar sincronização automática
@main.route('/sync/toggle-auto-sync', methods=['POST'])
def toggle_auto_sync():
    try:
        auto_sync = request.form.get('auto_sync') == 'true'
        
        # Salvar configuração
        config_file = Config.CONFIG_FILE
        config = {}
        
        if os.path.exists(config_file):
            with open(config_file, 'r') as f:
                config = json.load(f)
        
        config['auto_sync'] = auto_sync
        
        with open(config_file, 'w') as f:
            json.dump(config, f)
        
        flash('Configuração de sincronização automática salva com sucesso!', 'success')
        return redirect(url_for('main.sync'))
        
    except Exception as e:
        flash(f'Erro: {str(e)}', 'error')
        return redirect(url_for('main.sync'))

# Rota para logout
@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))
