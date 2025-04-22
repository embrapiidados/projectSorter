import os
from dotenv import load_dotenv
from puxar_planilhas_sharepoint import puxar_planilhas
from dados_tratamento import tratar_portfolio
from gerar_arquivos_json import gerar_arquivos_json
from levar_arquivos_json import levar_arquivos_json
import inspect

# carregar .env 
load_dotenv()
ROOT = os.getenv('ROOT')
PORTFOLIO = os.path.abspath(os.path.join(ROOT, 'inputs', 'portfolio.xlsx'))#


def main():
    print("🟡 " + inspect.currentframe().f_code.co_name)

    puxar_planilhas()
    tratar_portfolio()
    gerar_arquivos_json()
    levar_arquivos_json()

    print("🟢 " + inspect.currentframe().f_code.co_name)
    

if __name__ == "__main__":
    main()