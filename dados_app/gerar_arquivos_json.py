import os
from dotenv import load_dotenv
import pandas as pd
import inspect

# Carregar .env
load_dotenv()
ROOT = os.getenv('ROOT')

PORTFOLIO = os.path.abspath(os.path.join(ROOT, 'data_processed', 'portfolio_tratado.xlsx'))
AIA = os.path.abspath(os.path.join(ROOT, 'data_reference', 'classificacao_projetos_aia.xlsx'))
DATA_JSON = os.path.abspath(os.path.join(ROOT, 'data_json'))
os.makedirs(DATA_JSON, exist_ok=True)

COL_LISTAGEM_PROJETOS = (
    'codigo_projeto',
    'unidade_embrapii',
    'data_contrato',
    'status',
    'uso_recurso_obrigatorio',
    'titulo',
    '_fonte_recurso',
    '_sebrae',
    '_valor_total',
    '_perc_valor_embrapii',
    '_perc_valor_empresa_sebrae',
    '_perc_valor_unidade_embrapii',
)

# def json_listagem_projetos():
#     df_portfolio = pd.read_excel(PORTFOLIO)

#     # Filtrar as colunas desejadas
#     df_filtrado = df_portfolio[list(COL_LISTAGEM_PROJETOS)]

#     # Exportar como JSON
#     output_path = os.path.join(DATA_JSON, 'listagem_projetos.json')
#     df_filtrado.to_json(output_path, orient='records', force_ascii=False, indent=2)

def json_listagem_projetos_completo():
    df_portfolio = pd.read_excel(PORTFOLIO)

    # Exportar como JSON
    output_path = os.path.join(DATA_JSON, 'all_projetos.json')
    df_portfolio.to_json(output_path, orient='records', force_ascii=False, indent=2)

def json_aia():
    df = pd.read_excel(AIA)

    # Exportar como JSON
    output_path = os.path.join(DATA_JSON, 'aia.json')
    df.to_json(output_path, orient='records', force_ascii=False, indent=2)


def gerar_arquivos_json():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    
    # json_listagem_projetos()
    json_listagem_projetos_completo()
    json_aia()
    
    print("🟢 " + inspect.currentframe().f_code.co_name)
