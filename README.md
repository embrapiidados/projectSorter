# Sistema de Categorização de Projetos

## Visão Geral

Este é um microsistema para categorização de projetos, que utiliza uma planilha do SharePoint como banco de dados. O sistema foi projetado para ser empacotado e distribuído para até 5 usuários em computadores Windows.

## Funcionalidades

- **Autenticação segura** com SharePoint
- **Visualização de projetos** em uma interface moderna
- **Categorização de projetos** com suporte a diversas categorias:
  - Tecnologias Habilitadoras
  - Áreas de Aplicação
  - Microárea
  - Segmento
  - Domínio
- **Gerenciamento de listas** de categorias
- **Sugestão automática** de categorias usando IA via OpenAI (opcional)
- **Empacotamento fácil** para distribuição em Windows

## Estrutura da Planilha

O sistema utiliza uma planilha do SharePoint localizada em `General/Lucas Pinheiro/db_classificacao/db_classificacao_projeto.xlsx` com as seguintes abas:

1. **projetos** - Informações dos projetos
   - Colunas: id, codigo_projeto, codigo_interno, unidade_embrapii, tipo_projeto, status, titulo, titulo_publico, objetivo, descricao_publica, data_avaliacao, observacoes, tags

2. **categorias** - Categorização dos projetos
   - Colunas: id_projeto, tecnologias_habilitadoras, areas_aplicacao, microarea, segmento, dominio

3. **categorias_lists** - Listas de valores possíveis para categorias
   - Colunas: tecnologias_habilitadoras, areas_aplicacao, microarea, segmento, dominio

## Requisitos

- Python 3.8 ou superior
- Pip (gerenciador de pacotes Python)
- Acesso ao SharePoint
- Acesso à internet

## Instalação para Desenvolvimento

1. Clone o repositório:
   ```bash
   git clone <url-do-repositorio>
   cd sistema-categorizacao-projetos
   ```

2. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

3. Execute a aplicação:
   ```bash
   python run.py
   ```

## Empacotamento para Distribuição

Para criar uma versão executável para Windows:

1. Certifique-se de ter todas as dependências instaladas
   ```bash
   pip install -r requirements.txt
   ```

2. Execute o script de empacotamento:
   ```bash
   python build.py
   ```

3. O executável será criado na pasta `dist/CategoriasProjetos`

## Como Usar

1. Inicie a aplicação
2. Faça login com suas credenciais do SharePoint
3. Na tela de listagem de projetos, clique no botão "Categorizar" para o projeto desejado
4. Selecione as categorias apropriadas no formulário
5. Salve a categorização

### Sugestão Automática de Categorias

Para usar a funcionalidade de sugestão automática:

1. Acesse "Configurações" no menu da aplicação
2. Adicione sua chave da API da OpenAI
3. Ao categorizar um projeto, clique em "Sugerir Categorias com IA"

## Gerenciamento de Listas

Para gerenciar as listas de categorias disponíveis:

1. Acesse "Gerenciar Listas" no menu da aplicação
2. Adicione, remova ou edite as opções em cada categoria
3. Clique em "Salvar Todas as Listas" para atualizar no SharePoint

## Solução de Problemas

### Não consigo fazer login
- Verifique se suas credenciais do SharePoint estão corretas
- Verifique se a URL do site do SharePoint está correta

### Erro ao salvar categorias
- Verifique se você tem permissões de escrita no SharePoint
- Verifique se a planilha não está sendo editada por outra pessoa

### A sugestão automática não funciona
- Verifique se a chave da API da OpenAI foi configurada corretamente
- Verifique sua conexão com a internet

## Licença

Este software é licenciado para uso interno apenas. Todos os direitos reservados.