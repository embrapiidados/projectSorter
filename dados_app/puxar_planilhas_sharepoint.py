import os
import sys
from dotenv import load_dotenv
from office365_api.download_files import get_file
import inspect

# carregar .env e tudo mais
load_dotenv()
ROOT = os.getenv('ROOT')
PATH_OFFICE = os.path.abspath(os.path.join(ROOT, 'office365_api'))

# Adiciona o diretório correto ao sys.path
sys.path.append(PATH_OFFICE)

# puxar planilhas do sharepoint
def puxar_planilhas():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    
    inputs = os.path.join(ROOT, "inputs")
    data_processed = os.path.join(ROOT, "data_processed")
    data_json = os.path.join(ROOT, "data_json")
    apagar_arquivos_pasta(inputs)
    apagar_arquivos_pasta(data_processed)
    apagar_arquivos_pasta(data_json)

    get_file('portfolio.xlsx', 'DWPII/srinfo', inputs)

    
    print("🟢 " + inspect.currentframe().f_code.co_name)

def apagar_arquivos_pasta(caminho_pasta):
    try:
        # Verifica se o caminho é uma pasta; se não for, cria
        if not os.path.exists(caminho_pasta):
            os.makedirs(caminho_pasta)
            return
        
        # Lista todos os arquivos na pasta
        arquivos = os.listdir(caminho_pasta)
        
        # Apaga cada arquivo na pasta
        for arquivo in arquivos:
            caminho_arquivo = os.path.join(caminho_pasta, arquivo)
            if os.path.isfile(caminho_arquivo):
                os.remove(caminho_arquivo)
    except Exception as e:
        print(f"🔴 Ocorreu um erro ao apagar os arquivos: {e}")