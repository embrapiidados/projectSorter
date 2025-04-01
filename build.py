import os
import sys
import shutil
import subprocess
import platform

def clean_directories():
    """Limpa diretórios de builds anteriores."""
    print("Limpando diretórios de builds anteriores...")
    dirs_to_clean = ['build', 'dist']
    for dir_name in dirs_to_clean:
        if os.path.exists(dir_name):
            shutil.rmtree(dir_name)
    
    # Remover arquivos .spec
    for spec_file in [f for f in os.listdir('.') if f.endswith('.spec')]:
        os.remove(spec_file)

def install_dependencies():
    """Instala dependências necessárias."""
    print("Instalando dependências...")
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '-r', 'requirements.txt'])

def build_application():
    """Constrói a aplicação usando PyInstaller."""
    print("Construindo aplicação...")
    
    # Opções do PyInstaller
    pyinstaller_options = [
        'run.py',                      # Script principal
        '--name=CategoriasProjetos',   # Nome do executável
        '--onedir',                    # Criar um diretório único
        '--windowed',                  # Não mostrar console no Windows
        '--icon=app/static/favicon.ico', # Ícone da aplicação
        '--add-data=app/templates;app/templates',  # Incluir templates
        '--add-data=app/static;app/static',        # Incluir arquivos estáticos
        '--hidden-import=openpyxl',    # Importações ocultas
        '--hidden-import=flask',
        '--hidden-import=pandas',
        '--hidden-import=office365',
        '--hidden-import=openai'
    ]
    
    # Ajustar separadores de caminho para Windows
    if platform.system() == 'Windows':
        for i, option in enumerate(pyinstaller_options):
            if ';' in option:
                parts = option.split(';')
                pyinstaller_options[i] = f"{parts[0]};{parts[1]}"
    
    # Executar PyInstaller
    subprocess.check_call([sys.executable, '-m', 'PyInstaller'] + pyinstaller_options)

def create_config_folder():
    """Cria pasta de configuração na distribuição."""
    print("Criando pasta de configuração...")
    dist_path = os.path.join('dist', 'CategoriasProjetos')
    instance_path = os.path.join(dist_path, 'instance')
    
    if not os.path.exists(instance_path):
        os.makedirs(instance_path)

def create_readme():
    """Cria arquivo README com instruções."""
    print("Criando arquivo README...")
    readme_content = """
# Sistema de Categorização de Projetos

Este sistema permite categorizar projetos armazenados em uma planilha do SharePoint.

## Como usar

1. Execute o arquivo `CategoriasProjetos.exe`
2. Faça login com suas credenciais do SharePoint
3. Navegue pela lista de projetos e clique em "Categorizar" para um projeto
4. Escolha as categorias apropriadas e salve

## Recursos

- Autenticação segura com SharePoint
- Visualização e categorização de projetos
- Gerenciamento de listas de categorias
- Sugestão automática de categorias usando IA (requer chave da API OpenAI)

## Configuração da API OpenAI

Para habilitar a funcionalidade de sugestão automática de categorias:

1. Obtenha uma chave da API em https://platform.openai.com/account/api-keys
2. Acesse a página "Configurações" no sistema
3. Insira sua chave da API e salve

## Suporte

Em caso de problemas, verifique se:
- Você tem acesso à internet
- Suas credenciais do SharePoint estão corretas
- O caminho da planilha no SharePoint está correto: `General/Lucas Pinheiro/db_classificacao/db_classificacao_projeto.xlsx`
"""
    
    with open(os.path.join('dist', 'CategoriasProjetos', 'README.txt'), 'w', encoding='utf-8') as f:
        f.write(readme_content)

def create_favicon():
    """Cria um favicon básico para a aplicação."""
    print("Verificando favicon...")
    
    # Verificar se a pasta static existe
    static_dir = os.path.join('app', 'static')
    if not os.path.exists(static_dir):
        os.makedirs(static_dir)
    
    # Verificar se o favicon já existe
    favicon_path = os.path.join(static_dir, 'favicon.ico')
    if not os.path.exists(favicon_path):
        print("Favicon não encontrado. Criando um básico...")
        try:
            # Tenta usar PIL para criar um favicon básico
            from PIL import Image, ImageDraw
            
            img = Image.new('RGB', (48, 48), color=(13, 110, 253))  # Cor azul Bootstrap
            draw = ImageDraw.Draw(img)
            draw.rectangle([10, 10, 38, 38], fill=(255, 255, 255))  # Retângulo branco
            
            img.save(favicon_path)
            print("Favicon criado com sucesso.")
        except:
            print("Não foi possível criar o favicon. Continuando sem ele.")
            # Continue sem o favicon se PIL não estiver disponível

def main():
    """Função principal para construir a aplicação."""
    print("Iniciando empacotamento da aplicação...")
    
    # Verificar se estamos no diretório correto (onde está run.py)
    if not os.path.exists('run.py'):
        print("Erro: Execute este script no diretório raiz do projeto (onde está run.py)")
        sys.exit(1)
    
    # Criar favicon se não existir
    create_favicon()
    
    # Limpar diretórios anteriores
    clean_directories()
    
    # Instalar dependências
    install_dependencies()
    
    # Construir aplicação
    build_application()
    
    # Criar pasta de configuração
    create_config_folder()
    
    # Criar README
    create_readme()
    
    print("\nEmpacotamento concluído com sucesso!")
    print(f"Aplicação disponível em: {os.path.abspath(os.path.join('dist', 'CategoriasProjetos'))}")

if __name__ == "__main__":
    main()