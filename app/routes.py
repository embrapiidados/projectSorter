from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify, current_app
from app.json_data_client import JsonDataClient
from app.excel_manager import ExcelManager
from app.ai_integration import OpenAIClient
from config import Config
import json
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
        
        return render_template('projects.html', projects=projects_data)
        
    except Exception as e:
        flash(f'Erro ao carregar projetos: {str(e)}', 'error')
        return redirect(url_for('main.login'))

# Função para registrar log de categorização
def log_categorization(project_id, used_ai=False):
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
            'ia': 'Sim' if used_ai else 'Não'
        }
        
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

# Rota para categorização de um projeto
@main.route('/categorize/<project_id>', methods=['GET', 'POST'])
@main.route('/categorize/<project_id>/', methods=['GET', 'POST'])
def categorize(project_id):
    try:
        json_client = JsonDataClient()
        
        if request.method == 'POST':
            # Processar o formulário de categorização
            category_data = {
                'id_projeto': project_id,  # Agora usando codigo_projeto como identificador
                'tecnologias_habilitadoras': request.form.get('tecnologias_habilitadoras'),
                'areas_aplicacao': request.form.get('areas_aplicacao'),
                'microarea': request.form.get('microarea'),
                'segmento': request.form.get('segmento'),
                'dominio': request.form.get('dominio')
            }
            
            # Verificar se utilizou a IA (através de um campo oculto no form)
            used_ai = request.form.get('used_ai') == 'true'
            
            # Atualizar categorização no arquivo JSON
            json_client.update_excel_data(
                None,
                'categorias',
                category_data,
                'id_projeto'
            )
            
            # Registrar log da categorização
            log_categorization(project_id, used_ai)
            
            flash('Categorização salva com sucesso!', 'success')
            return redirect(url_for('main.projects'))
        
        # Obter dados do projeto
        project = json_client.get_project_by_id(
            None,
            project_id
        )
        
        if not project:
            flash('Projeto não encontrado', 'error')
            return redirect(url_for('main.projects'))
        
        # Obter listas de categorias
        categories_lists = json_client.get_excel_data(
            None,
            'categorias_lists'
        )
        
        # Organizar as listas por tipo
        organized_lists = {}
        for column in ['tecnologias_habilitadoras', 'areas_aplicacao', 'microarea', 'segmento', 'dominio']:
            organized_lists[column] = list(set([item.get(column, '') for item in categories_lists if item.get(column)]))
        
        # Obter categorização existente
        existing = json_client.get_categorization_by_project_id(
            None,
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
        
        # Chamar OpenAI para sugerir categorias
        openai_client = OpenAIClient(openai_api_key)
        suggestions = openai_client.suggest_categories(project, organized_lists)
        
        return jsonify(suggestions)
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

# Rota para lidar com /categorize/ sem project_id
@main.route('/categorize/', methods=['GET'])
def categorize_no_id():
    flash('É necessário selecionar um projeto para categorizar', 'warning')
    return redirect(url_for('main.projects'))

# Rota para logout
@main.route('/logout')
def logout():
    session.clear()
    return redirect(url_for('main.login'))
