
import os
from dotenv import load_dotenv
import pandas as pd
import inspect

# carregar .env 
load_dotenv()
ROOT = os.getenv('ROOT')
PORTFOLIO = os.path.abspath(os.path.join(ROOT, 'inputs', 'portfolio.xlsx'))

DATA_PROCESSED = os.path.abspath(os.path.join(ROOT, 'data_processed'))
os.makedirs(DATA_PROCESSED, exist_ok=True)

DIC_FONTE = {
        "BNDES": "BNDES",
        "BNDES Bioeconomia Florestal": "BNDES",
        "BNDES Bioeconomia Florestal; SEBRAE Ciclo Integrado": "BNDES",
        "BNDES Bioeconomia Florestal; SEBRAE Ciclo Integrado 4º Contrato": "BNDES",
        "BNDES Defesa": "BNDES",
        "BNDES Defesa; SEBRAE Ciclo Integrado 4º Contrato": "BNDES",
        "BNDES Economia Circular": "BNDES",
        "BNDES Economia Circular; SEBRAE Ciclo Integrado": "BNDES",
        "BNDES Materiais Avançados": "BNDES",
        "BNDES Novos Biocombustíveis": "BNDES",
        "BNDES Novos Biocombustíveis; SEBRAE Ciclo Integrado 4º Contrato": "BNDES",
        "BNDES Tec. Estratégicas SUS": "BNDES",
        "BNDES Tec. Estratégicas SUS; SEBRAE Ciclo Integrado": "BNDES",
        "BNDES Trans. Digital - Conectividade": "BNDES",
        "BNDES Trans. Digital - Conectividade; SEBRAE Ciclo Integrado": "BNDES",
        "BNDES Trans. Digital - Conectividade; SEBRAE Ciclo Integrado 4º Contrato": "BNDES",
        "BNDES Trans. Digital - Soluções Digitais": "BNDES",
        "BNDES Trans. Digital - Soluções Digitais; SEBRAE Ciclo Integrado": "BNDES",
        "BNDES Trans. Digital - Soluções Digitais; SEBRAE Ciclo Integrado 4º Contrato": "BNDES",
        "EMBRAPII CG": "CG",
        "EMBRAPII CG Ciclo2": "CG",
        "EMBRAPII CG Ciclo2; SEBRAE Ciclo 2": "CG",
        "Ministério da Saúde": "CG",
        "PPI": "PPI",
        "ROTA 2030": "Mover",
        "ROTA 2030 Estruturante": "Mover",
        "ROTA 2030 Startup": "Mover",
        "ROTA 2030; SEBRAE CG": "Mover",
        "ROTA 2030; SEBRAE Ciclo Integrado": "Mover",
        "ROTA 2030; SEBRAE Ciclo Integrado 4º Contrato": "Mover",
        "SEBRAE CG": "CG",
        "SEBRAE CG; BNDES Trans. Digital - Soluções Digitais": "BNDES",
        "SEBRAE Ciclo 2": "CG",
        "SEBRAE Ciclo Integrado": "CG",
        "SEBRAE Ciclo Integrado 4º Contrato": "CG",
}

DIC_SEBRAE = {
        "BNDES": "Não",
        "BNDES Bioeconomia Florestal": "Não",
        "BNDES Bioeconomia Florestal; SEBRAE Ciclo Integrado": "Sim",
        "BNDES Bioeconomia Florestal; SEBRAE Ciclo Integrado 4º Contrato": "Sim",
        "BNDES Defesa": "Não",
        "BNDES Defesa; SEBRAE Ciclo Integrado 4º Contrato": "Sim",
        "BNDES Economia Circular": "Não",
        "BNDES Economia Circular; SEBRAE Ciclo Integrado": "Sim",
        "BNDES Materiais Avançados": "Não",
        "BNDES Novos Biocombustíveis": "Não",
        "BNDES Novos Biocombustíveis; SEBRAE Ciclo Integrado 4º Contrato": "Sim",
        "BNDES Tec. Estratégicas SUS": "Não",
        "BNDES Tec. Estratégicas SUS; SEBRAE Ciclo Integrado": "Sim",
        "BNDES Trans. Digital - Conectividade": "Não",
        "BNDES Trans. Digital - Conectividade; SEBRAE Ciclo Integrado": "Sim",
        "BNDES Trans. Digital - Conectividade; SEBRAE Ciclo Integrado 4º Contrato": "Sim",
        "BNDES Trans. Digital - Soluções Digitais": "Não",
        "BNDES Trans. Digital - Soluções Digitais; SEBRAE Ciclo Integrado": "Sim",
        "BNDES Trans. Digital - Soluções Digitais; SEBRAE Ciclo Integrado 4º Contrato": "Sim",
        "EMBRAPII CG": "Não",
        "EMBRAPII CG Ciclo2": "Não",
        "EMBRAPII CG Ciclo2; SEBRAE Ciclo 2": "Sim",
        "Ministério da Saúde": "Não",
        "PPI": "Não",
        "ROTA 2030": "Não",
        "ROTA 2030 Estruturante": "Não",
        "ROTA 2030 Startup": "Não",
        "ROTA 2030; SEBRAE CG": "Sim",
        "ROTA 2030; SEBRAE Ciclo Integrado": "Sim",
        "ROTA 2030; SEBRAE Ciclo Integrado 4º Contrato": "Sim",
        "SEBRAE CG": "Sim",
        "SEBRAE CG; BNDES Trans. Digital - Soluções Digitais": "Sim",
        "SEBRAE Ciclo 2": "Sim",
        "SEBRAE Ciclo Integrado": "Sim",
        "SEBRAE Ciclo Integrado 4º Contrato": "Sim",
}

def tratar_portfolio():
    print("🟡 " + inspect.currentframe().f_code.co_name)
    
    df_portfolio = pd.read_excel(PORTFOLIO)

    #Novas classificações
    df_portfolio["_fonte_recurso"] = df_portfolio["parceria_programa"].map(DIC_FONTE)
    df_portfolio["_sebrae"] = df_portfolio["parceria_programa"].map(DIC_SEBRAE)
    
    # Valor total
    df_portfolio["_valor_total"] = df_portfolio[[
        "valor_embrapii", 
        "valor_empresa", 
        "valor_unidade_embrapii", 
        "valor_sebrae"
    ]].sum(axis=1)

    # Percentuais
    df_portfolio["_perc_valor_embrapii"] = df_portfolio["valor_embrapii"] / df_portfolio["_valor_total"]
    df_portfolio["_perc_valor_empresa"] = df_portfolio["valor_empresa"] / df_portfolio["_valor_total"]
    df_portfolio["_perc_valor_sebrae"] = df_portfolio["valor_sebrae"] / df_portfolio["_valor_total"]
    df_portfolio["_perc_valor_unidade_embrapii"] = df_portfolio["valor_unidade_embrapii"] / df_portfolio["_valor_total"]
    df_portfolio["_perc_valor_empresa_sebrae"] = (df_portfolio["valor_empresa"] + df_portfolio["valor_sebrae"]) / df_portfolio["_valor_total"]

    #Novos campos
    df_portfolio["_aia_n1_macroarea"] = ""
    df_portfolio["_aia_n2_segmento"] = ""
    df_portfolio["_aia_n3_dominio_afeito"] = ""
    df_portfolio["_aia_n3_dominio_outro"] = ""
    
    df_portfolio = df_portfolio.sort_values(by="data_contrato", ascending=False)
    output_path = os.path.join(DATA_PROCESSED, "portfolio_tratado.xlsx")
    df_portfolio.to_excel(output_path, index=False)
    
    print("🟢 " + inspect.currentframe().f_code.co_name)