from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from app.sharepoint_client import SharePointClient
from app.excel_manager import ExcelManager
from app.ai_integration import OpenAIClient
from config import Config
import json
from datetime import datetime

main = Blueprint('main', __name__)

# Middleware para verificar autenticação
@main.before_request
def check_auth():
    # Ignorar verificação para rotas de login
    if request.endpoint in ['main.login', 'main.static']:
        return
    
    # Verificar se o usuário está autenticado
    if 'sharepoint_username' not in session:
        return redirect(url_for('main.login'))

# Rota para a página inicial
@main.route('/')
def index():
    return redirect(url_for('main.projects'))

# Rota para login
@main.route('/login', methods=['GET', 'POST'])
def login():
    error = None
    
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        site_url = request.form.get('site_url')
        
        try:
            # Tentar autenticar com o SharePoint
            sp_client = SharePointClient(site_url, username, password)
            
            # Se chegar aqui, a autenticação foi bem-sucedida
            session['sharepoint_username'] = username
            session['sharepoint_password'] = password
            session['sharepoint_site_url'] = site_url
            
            return redirect(url_for('main.projects'))
            
        except Exception as e:
            error = str(e)
    
    return render_template('login.html', error=error)

# Rota para listagem de projetos
@main.route('/projects')
def projects():
    try:
        sp_client = SharePointClient(
            session['sharepoint_site_url'],
            session['sharepoint_username'],
            session['sharepoint_password']
        )
        
        # Obter dados dos projetos
        excel_path = Config.SHAREPOINT_EXCEL_PATH
        
        # Log do caminho para debug
        print(f"Tentando acessar planilha: {excel_path}")
        
        projects_data = sp_client.get_excel_data(
            excel_path,
            'projetos'
        )
        
        return render_template('projects.html', projects=projects_data)
        
    except Exception as e:
        flash(f'Erro ao carregar projetos: {str(e)}', 'error')
        return redirect(url_for('main.login'))

# Função para registrar log de categorização
def log_categorization(project_id, used_ai=False):
    try:
        sp_client = SharePointClient(
            session['sharepoint_site_url'],
            session['sharepoint_username'],
            session['sharepoint_password']
        )
        
        # Obter logs existentes para determinar próximo ID
        try:
            logs = sp_client.get_excel_data(
                Config.SHAREPOINT_EXCEL_PATH,
                'logs'
            )
            # Determinar o próximo ID
            next_id = 1
            if logs and len(logs) > 0:
                ids = [log.get('id', 0) for log in logs]
                next_id = max(ids) + 1
        except Exception as e:
            # Se a aba não existir ou ocorrer erro, começar do ID 1
            print(f"Aviso: Não foi possível ler logs existentes: {str(e)}")
            logs = []
            next_id = 1
        
        # Criar registro de log
        log_data = {
            'id': next_id,
            'id_projeto': project_id,
            'email': session['sharepoint_username'],
            'data': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'ia': 'Sim' if used_ai else 'Não'
        }
        
        # Adicionar o log à planilha
        if logs:
            # Adicionar ao final da lista existente
            logs.append(log_data)
            sp_client.update_excel_data(
                Config.SHAREPOINT_EXCEL_PATH,
                'logs',
                logs
            )
        else:
            # Criar lista com apenas este log
            sp_client.update_excel_data(
                Config.SHAREPOINT_EXCEL_PATH,
                'logs',
                [log_data]
            )
        
        print(f"Log de categorização registrado: {log_data}")
        return True
    except Exception as e:
        print(f"Erro ao registrar log de categorização: {str(e)}")
        return False

# Rota para categorização de um projeto
@main.route('/categorize/<project_id>', methods=['GET', 'POST'])
def categorize(project_id):
    try:
        sp_client = SharePointClient(
            session['sharepoint_site_url'],
            session['sharepoint_username'],
            session['sharepoint_password']
        )
        
        if request.method == 'POST':
            # Processar o formulário de categorização
            category_data = {
                'id_projeto': project_id,
                'tecnologias_habilitadoras': request.form.get('tecnologias_habilitadoras'),
                'areas_aplicacao': request.form.get('areas_aplicacao'),
                'microarea': request.form.get('microarea'),
                'segmento': request.form.get('segmento'),
                'dominio': request.form.get('dominio')
            }
            
            # Verificar se utilizou a IA (através de um campo oculto no form)
            used_ai = request.form.get('used_ai') == 'true'
            
            # Atualizar categorização no SharePoint
            sp_client.update_excel_data(
                Config.SHAREPOINT_EXCEL_PATH,
                'categorias',
                category_data,
                'id_projeto'
            )
            
            # Registrar log da categorização
            log_categorization(project_id, used_ai)
            
            flash('Categorização salva com sucesso!', 'success')
            return redirect(url_for('main.projects'))
        
        # Obter dados do projeto
        project = sp_client.get_project_by_id(
            Config.SHAREPOINT_EXCEL_PATH,
            project_id
        )
        
        if not project:
            flash('Projeto não encontrado', 'error')
            return redirect(url_for('main.projects'))
        
        # Obter listas de categorias
        categories_lists = sp_client.get_excel_data(
            Config.SHAREPOINT_EXCEL_PATH,
            'categorias_lists'
        )
        
        # Organizar as listas por tipo
        organized_lists = {}
        for column in ['tecnologias_habilitadoras', 'areas_aplicacao', 'microarea', 'segmento', 'dominio']:
            organized_lists[column] = list(set([item.get(column, '') for item in categories_lists if item.get(column)]))
        
        # Obter categorização existente
        existing = sp_client.get_categorization_by_project_id(
            Config.SHAREPOINT_EXCEL_PATH,
            project_id
        )
        
        # Verificar se a chave da OpenAI está configurada
        openai_api_key = Config.get_openai_api_key()
        
        return render_template(
            'categorize.html',
            project=project,
            categories_lists=organized_lists,
            existing=existing,
            openai_enabled=(openai_api_key != '')
        )
        
    except Exception as e:
        flash(f'Erro: {str(e)}', 'error')
        return redirect(url_for('main.projects'))

# Rota para gerenciar listas de categorias
@main.route('/lists', methods=['GET', 'POST'])
def lists():
    try:
        sp_client = SharePointClient(
            session['sharepoint_site_url'],
            session['sharepoint_username'],
            session['sharepoint_password']
        )
        
        if request.method == 'POST':
            # Processar o formulário de atualização de listas
            lists_data = {}
            
            for column in ['tecnologias_habilitadoras', 'areas_aplicacao', 'microarea', 'segmento', 'dominio']:
                values = request.form.getlist(f'{column}[]')
                # Filtrar valores vazios
                values = [v for v in values if v.strip()]
                lists_data[column] = values
            
            # Converter para o formato esperado pelo Excel
            excel_data = []
            max_length = max(len(values) for values in lists_data.values())
            
            for i in range(max_length):
                row = {}
                for column, values in lists_data.items():
                    row[column] = values[i] if i < len(values) else None
                excel_data.append(row)
            
            # Atualizar no SharePoint
            sp_client.update_excel_data(
                Config.SHAREPOINT_EXCEL_PATH,
                'categorias_lists',
                excel_data
            )
            
            flash('Listas atualizadas com sucesso!', 'success')
            return redirect(url_for('main.lists'))
        
        # Obter listas de categorias
        categories_lists = sp_client.get_excel_data(
            Config.SHAREPOINT_EXCEL_PATH,
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
        sp_client = SharePointClient(
            session['sharepoint_site_url'],
            session['sharepoint_username'],
            session['sharepoint_password']
        )
        
        # Obter logs
        try:
            logs = sp_client.get_excel_data(
                Config.SHAREPOINT_EXCEL_PATH,
                'logs'
            )
        except Exception as e:
            print(f"Erro ao obter logs: {str(e)}")
            logs = []
        
        # Obter projetos para exibir nomes em vez de IDs
        projects = sp_client.get_excel_data(
            Config.SHAREPOINT_EXCEL_PATH,
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
        
        # Conectar ao SharePoint
        sp_client = SharePointClient(
            session['sharepoint_site_url'],
            session['sharepoint_username'],
            session['sharepoint_password']
        )
        
        # Obter dados do projeto
        project = sp_client.get_project_by_id(
            Config.SHAREPOINT_EXCEL_PATH,
            project_id
        )
        
        if not project:
            return jsonify({'error': 'Projeto não encontrado'}), 404
        
        # Obter listas de categorias
        categories_lists_data = sp_client.get_excel_data(
            Config.SHAREPOINT_EXCEL_PATH,
            'categorias_lists'
        )
        
        # Organizar as listas por tipo
        organized_lists = {}
        for column in ['tecnologias_habilitadoras', 'areas_aplicacao', 'microarea', 'segmento', 'dominio']:
            organized_lists[column] = list(set([item.get(column, '') for item in categories_lists_data if item.get(column)]))
        
        # Chamar OpenAI para sugerir categorias
        openai_client = OpenAIClient(openai_api_key)
        suggestions = openai_client.suggest_categories(project, organized_lists)
        
        return jsonify(suggestions)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para logout
@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))