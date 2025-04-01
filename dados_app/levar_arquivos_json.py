import os
import shutil
from dotenv import load_dotenv
import inspect

# Carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')
DATA_APP = os.getenv('DATA_APP')
FOLDER_JSON = os.path.abspath(os.path.join(ROOT, 'data_json'))

def levar_arquivos_json():
    print("🟡 " + inspect.currentframe().f_code.co_name)

    if not os.path.exists(FOLDER_JSON):
        print(f"Pasta de origem não encontrada: {FOLDER_JSON}")
        return

    if not os.path.exists(DATA_APP):
        os.makedirs(DATA_APP, exist_ok=True)
        print(f"Pasta de destino criada: {DATA_APP}")

    arquivos = os.listdir(FOLDER_JSON)
    for arquivo in arquivos:
        origem = os.path.join(FOLDER_JSON, arquivo)
        destino = os.path.join(DATA_APP, arquivo)
        if os.path.isfile(origem):
            shutil.copy2(origem, destino)
    
    print("🟢 " + inspect.currentframe().f_code.co_name)


