import os
import json
from dotenv import load_dotenv
from puxar_planilhas_sharepoint import puxar_planilhas
from dados_tratamento import tratar_portfolio
from gerar_arquivos_json import json_listagem_projetos_completo, json_aia
import inspect

# Campos de categorização que devem ser preservados
CAMPOS_CATEGORIZACAO = [
    '_aia_n1_macroarea',
    '_aia_n2_segmento',
    '_aia_n3_dominio_afeito',
    '_aia_n3_dominio_outro',
    'tecnologia_habilitadora',
    'area_aplicacao',
    'observacoes'
]

def mesclar_projetos():
    """
    Mescla os novos projetos com os existentes, preservando categorizações.
    """
    # Carregar .env
    load_dotenv()
    ROOT = os.getenv('ROOT')
    DATA_APP = os.getenv('DATA_APP')
    
    # Caminhos dos arquivos
    json_temp = os.path.join(ROOT, 'data_json', 'all_projetos.json')
    json_app = os.path.join(DATA_APP, 'all_projetos.json')
    
    print(f"🔍 Mesclando projetos de {json_temp} com {json_app}")
    
    # Verificar se o arquivo da aplicação existe
    if not os.path.exists(json_app):
        print(f"⚠️ Arquivo {json_app} não existe. Criando novo arquivo.")
        # Se não existir, apenas copiar o arquivo temporário
        os.makedirs(os.path.dirname(json_app), exist_ok=True)
        with open(json_temp, 'r', encoding='utf-8') as f:
            novos_projetos = json.load(f)
        with open(json_app, 'w', encoding='utf-8') as f:
            json.dump(novos_projetos, f, ensure_ascii=False, indent=2)
        print(f"✅ {len(novos_projetos)} projetos adicionados ao novo arquivo.")
        return
    
    # Carregar projetos existentes
    with open(json_app, 'r', encoding='utf-8') as f:
        projetos_existentes = json.load(f)
    
    # Carregar novos projetos
    with open(json_temp, 'r', encoding='utf-8') as f:
        novos_projetos = json.load(f)
    
    print(f"📊 Encontrados {len(projetos_existentes)} projetos existentes e {len(novos_projetos)} novos projetos.")
    
    # Criar dicionário de projetos existentes para fácil acesso
    dict_existentes = {str(p.get('codigo_projeto')): p for p in projetos_existentes}
    
    # Lista para armazenar projetos mesclados
    projetos_mesclados = []
    
    # Contadores para estatísticas
    contador_novos = 0
    contador_atualizados = 0
    contador_preservados = 0
    
    # Processar novos projetos
    for novo_projeto in novos_projetos:
        codigo = str(novo_projeto.get('codigo_projeto'))
        
        if codigo in dict_existentes:
            # Projeto já existe, preservar categorizações
            projeto_existente = dict_existentes[codigo]
            
            # Criar cópia do novo projeto
            projeto_mesclado = novo_projeto.copy()
            
            # Verificar se há campos de categorização preenchidos
            tem_categorizacao = False
            
            # Preservar campos de categorização se estiverem preenchidos
            for campo in CAMPOS_CATEGORIZACAO:
                if campo in projeto_existente and projeto_existente.get(campo):
                    projeto_mesclado[campo] = projeto_existente.get(campo)
                    tem_categorizacao = True
            
            projetos_mesclados.append(projeto_mesclado)
            
            # Contabilizar estatísticas
            if tem_categorizacao:
                contador_preservados += 1
            else:
                contador_atualizados += 1
            
            # Remover do dicionário para controle
            del dict_existentes[codigo]
        else:
            # Projeto novo, adicionar diretamente
            projetos_mesclados.append(novo_projeto)
            contador_novos += 1
    
    # Adicionar projetos que existiam mas não estão nos novos
    # (isso pode acontecer se um projeto for removido da fonte)
    for projeto_restante in dict_existentes.values():
        projetos_mesclados.append(projeto_restante)
    
    # Ordenar projetos por data_contrato (decrescente)
    projetos_mesclados.sort(key=lambda x: x.get('data_contrato', ''), reverse=True)
    
    # Salvar arquivo mesclado
    with open(json_app, 'w', encoding='utf-8') as f:
        json.dump(projetos_mesclados, f, ensure_ascii=False, indent=2)
    
    print(f"✅ Mesclagem concluída:")
    print(f"   - {contador_novos} novos projetos adicionados")
    print(f"   - {contador_atualizados} projetos atualizados sem categorização")
    print(f"   - {contador_preservados} projetos atualizados com categorização preservada")
    print(f"   - {len(dict_existentes)} projetos mantidos que não estão na nova fonte")
    print(f"   - Total: {len(projetos_mesclados)} projetos no arquivo final")

def atualizar_projetos():
    print("🟡 " + inspect.currentframe().f_code.co_name)

    # Executar as etapas do processo original
    puxar_planilhas()
    tratar_portfolio()
    
    # Gerar arquivos JSON temporários
    json_listagem_projetos_completo()
    json_aia()
    
    # Mesclar projetos preservando categorizações
    mesclar_projetos()
    
    print("🟢 " + inspect.currentframe().f_code.co_name)

if __name__ == "__main__":
    atualizar_projetos()
