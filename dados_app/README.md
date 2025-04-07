# dados_app

Este diretório contém scripts para gerar arquivos JSON na pasta `app/data`.

## Arquivos Principais

- `main.py`: Script original que baixa planilhas do SharePoint, processa os dados e gera arquivos JSON.
- `generate_json.py`: Script simplificado que gera arquivos JSON sem necessidade de conexão com SharePoint.
- `atualizar_projetos.py`: Script que atualiza o arquivo JSON com novos projetos sem sobrescrever categorizações existentes.

## Requisitos

- Python 3.x
- Pacotes Python listados em `requirements.txt`
- Arquivo `.env` na raiz do projeto com as seguintes variáveis:
  - `ROOT`: Caminho para o diretório raiz do dados_app
  - `DATA_APP`: Caminho para o diretório app/data
  
  Para o script original `main.py` (com SharePoint), também são necessárias:
  - `sharepoint_email`: Email para autenticação no SharePoint
  - `sharepoint_password`: Senha para autenticação no SharePoint
  - `sharepoint_url_site`: URL do site SharePoint (ex: https://seusite.sharepoint.com)
  - `sharepoint_site_name`: Nome do site SharePoint
  - `sharepoint_doc_library`: Nome da biblioteca de documentos no SharePoint (geralmente "Documentos" ou "Documents")

## Como Usar

### Usando o script simplificado (sem SharePoint)

```bash
python generate_json.py
```

Este script:
1. Cria os diretórios necessários
2. Copia os arquivos JSON existentes para processamento
3. Gera os arquivos JSON na pasta `app/data`

### Usando o script original (com SharePoint)

```bash
python main.py
```

Este script requer credenciais do SharePoint no arquivo `.env`:
- `sharepoint_email`
- `sharepoint_password`
- `sharepoint_url_site`
- `sharepoint_site_name`
- `sharepoint_doc_library`

### Usando o script de atualização (preserva categorizações)

```bash
python atualizar_projetos.py
```

Este script:
1. Baixa planilhas do SharePoint (como o script original)
2. Processa os dados do portfólio
3. Gera arquivos JSON temporários
4. Mescla os novos dados com o arquivo JSON existente, preservando categorizações já realizadas
5. Atualiza o arquivo JSON na pasta `app/data`

**Importante**: Diferente do script `main.py`, este script não sobrescreve as categorizações já realizadas nos projetos existentes.

### Testando a funcionalidade de mesclagem

```bash
python testar_mesclagem.py
```

Este script de teste:
1. Cria dados de teste simulando projetos existentes (com categorizações) e novos projetos
2. Executa a função de mesclagem em um ambiente isolado
3. Exibe o resultado da mesclagem, mostrando como as categorizações são preservadas
4. Não afeta os dados reais da aplicação

Útil para verificar o comportamento da mesclagem sem precisar conectar ao SharePoint.

## Estrutura de Diretórios

- `inputs/`: Onde as planilhas do SharePoint são baixadas
- `data_processed/`: Onde os dados processados são armazenados
- `data_json/`: Onde os arquivos JSON são gerados antes de serem copiados para `app/data`

## Arquivos JSON Gerados

- `all_projetos.json`: Contém dados de todos os projetos
- `aia.json`: Contém dados de classificação AIA
- Outros arquivos JSON conforme necessário
