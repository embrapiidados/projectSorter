from openai import OpenAI
import json
from datetime import datetime

class OpenAIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        self.client = OpenAI(api_key=api_key)
    
    def suggest_categories(self, project, categories_lists=None, aia_data=None):
        """
        Sugere categorias para um projeto usando a API do OpenAI em um processo de duas etapas.
        
        Etapa 1: A IA identifica a Micro Área, Segmento e Domínio
        Etapa 2: Com base nessas informações, fornecemos a lista correta de Domínios Afeitos Outros
                 (todos os domínios de outros segmentos da mesma microárea) para a IA selecionar
        
        Args:
            project: Dicionário com informações do projeto
            categories_lists: Dicionário com as listas de categorias disponíveis (opcional)
            aia_data: Lista de categorias do arquivo aia.json (opcional)
            
        Returns:
            Dicionário com as categorias sugeridas e informações adicionais
        """
        if not self.api_key:
            return {
                "error": "Chave da API OpenAI não configurada"
            }
        
        try:
            # ETAPA 1: Identificar Micro Área, Segmento e Domínio
            prompt_etapa1 = self._build_prompt_etapa1(project, aia_data)
            
            # Chamar a API do ChatGPT para a primeira etapa
            response_etapa1 = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em categorizar projetos de pesquisa e desenvolvimento."},
                    {"role": "user", "content": prompt_etapa1}
                ],
                temperature=0.3,
                max_tokens=800
            )
            
            # Extrair a resposta da primeira etapa
            ai_response_etapa1 = response_etapa1.choices[0].message.content.strip()
            
            # Processar a resposta da primeira etapa
            try:
                # Tentar analisar como JSON
                result_etapa1 = self._parse_ai_response(ai_response_etapa1)
                
                # Se não conseguiu obter um resultado válido, retornar erro
                if not result_etapa1 or "error" in result_etapa1:
                    return result_etapa1
                
                # ETAPA 2: Fornecer a lista de Domínios Afeitos Outros para seleção
                # Extrair a microárea e segmento identificados na primeira etapa
                macroarea = result_etapa1.get("_aia_n1_macroarea", "")
                segmento = result_etapa1.get("_aia_n2_segmento", "")
                
                # Se não temos microárea ou segmento, não podemos continuar
                if not macroarea or not segmento:
                    result_etapa1["_aia_n3_dominio_outro"] = "N/A"
                    result_etapa1["timestamp"] = datetime.now().isoformat()
                    return result_etapa1
                
                # Gerar a lista de Domínios Afeitos Outros (todos os domínios de outros segmentos da mesma microárea)
                dominios_afeitos_outros = self._get_dominios_afeitos_outros(macroarea, segmento, aia_data)
                
                # Verificar se a lista de domínios afeitos outros está vazia
                if not dominios_afeitos_outros:
                    # Se não há domínios afeitos outros, definir como N/A e pular etapa 2
                    result_etapa1["_aia_n3_dominio_outro"] = "N/A"
                    result_etapa1["timestamp"] = datetime.now().isoformat()
                    return result_etapa1
                
                # Construir o prompt para a segunda etapa (só será executado se houver domínios afeitos outros)
                prompt_etapa2 = self._build_prompt_etapa2(project, result_etapa1, dominios_afeitos_outros)
                
                # Chamar a API do ChatGPT para a segunda etapa
                response_etapa2 = self.client.chat.completions.create(
                    model="gpt-3.5-turbo",
                    messages=[
                        {"role": "system", "content": "Você é um assistente especializado em categorizar projetos de pesquisa e desenvolvimento."},
                        {"role": "user", "content": prompt_etapa2}
                    ],
                    temperature=0.3,
                    max_tokens=800
                )
                
                # Extrair a resposta da segunda etapa
                ai_response_etapa2 = response_etapa2.choices[0].message.content.strip()
                
                # Processar a resposta da segunda etapa
                result_etapa2 = self._parse_ai_response(ai_response_etapa2)
                
                # Combinar os resultados das duas etapas
                final_result = result_etapa1.copy()
                if result_etapa2 and "_aia_n3_dominio_outro" in result_etapa2:
                    final_result["_aia_n3_dominio_outro"] = result_etapa2["_aia_n3_dominio_outro"]
                
                # Adicionar timestamp
                final_result["timestamp"] = datetime.now().isoformat()
                return final_result
                
            except Exception as e:
                return {
                    "_aia_n1_macroarea": "",
                    "_aia_n2_segmento": "",
                    "_aia_n3_dominio_afeito": "",
                    "_aia_n3_dominio_outro": "",
                    "confianca": "BAIXA",
                    "justificativa": f"Erro ao processar resposta da IA: {str(e)}",
                    "error": f"Erro ao processar resposta da IA: {str(e)}",
                    "timestamp": datetime.now().isoformat()
                }
                
        except Exception as e:
            return {
                "_aia_n1_macroarea": "",
                "_aia_n2_segmento": "",
                "_aia_n3_dominio_afeito": "",
                "_aia_n3_dominio_outro": "",
                "confianca": "BAIXA",
                "justificativa": "",
                "error": f"Erro ao chamar OpenAI: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
    
    def _parse_ai_response(self, ai_response):
        """
        Analisa a resposta da IA e tenta extrair o JSON.
        
        Args:
            ai_response: Resposta da IA em texto
            
        Returns:
            Dicionário com os dados extraídos ou objeto de erro
        """
        try:
            # Tentar analisar como JSON diretamente
            result = json.loads(ai_response)
            return result
        except json.JSONDecodeError:
            # Tentar extrair apenas a parte JSON da resposta
            start_idx = ai_response.find('{')
            end_idx = ai_response.rfind('}') + 1
            
            if start_idx >= 0 and end_idx > 0:
                json_str = ai_response[start_idx:end_idx]
                try:
                    result = json.loads(json_str)
                    return result
                except:
                    pass
            
            # Retornar um objeto de erro se não conseguir extrair como JSON
            return {
                "_aia_n1_macroarea": "",
                "_aia_n2_segmento": "",
                "_aia_n3_dominio_afeito": "",
                "_aia_n3_dominio_outro": "",
                "confianca": "BAIXA",
                "justificativa": "Não foi possível processar a resposta da IA como JSON",
                "error": "Não foi possível processar a resposta da IA como JSON"
            }
    
    def _get_dominios_afeitos_outros(self, macroarea, segmento, aia_data):
        """
        Gera a lista de Domínios Afeitos Outros (todos os domínios de outros segmentos da mesma microárea).
        
        Args:
            macroarea: Microárea identificada
            segmento: Segmento identificado
            aia_data: Lista de categorias do arquivo aia.json
            
        Returns:
            Lista de domínios afeitos outros
        """
        if not aia_data:
            return []
        
        dominios_outros = []
        
        # Percorrer todos os itens do aia_data
        for item in aia_data:
            # Verificar se o item pertence à mesma microárea, mas a um segmento diferente
            if item.get('Macroárea') == macroarea and item.get('Segmento') != segmento:
                # Obter os domínios afeitos deste segmento
                dominios = item.get('Domínios Afeitos', '').split(';')
                # Adicionar à lista de domínios afeitos outros
                for dominio in dominios:
                    dominio = dominio.strip()
                    if dominio and dominio not in dominios_outros:
                        dominios_outros.append(dominio)
        
        return dominios_outros
    
    def _build_prompt_etapa1(self, project, aia_data=None):
        """
        Constrói o prompt para a primeira etapa: identificação de Micro Área, Segmento e Domínio.
        
        Args:
            project: Dicionário com informações do projeto
            aia_data: Lista de categorias do arquivo aia.json (opcional)
            
        Returns:
            String com o prompt formatado
        """
        # Construir a parte do prompt com as categorias do aia.json
        aia_categories_text = ""
        
        if aia_data:
            aia_categories_text = "Categorias do AIA (Áreas de Interesse Aplicado):\n\n"
            
            # Agrupar por Macroárea
            macroareas = {}
            for item in aia_data:
                macroarea = item.get('Macroárea')
                if macroarea not in macroareas:
                    macroareas[macroarea] = {}
                
                segmento = item.get('Segmento')
                if segmento not in macroareas[macroarea]:
                    macroareas[macroarea][segmento] = []
                
                dominios = item.get('Domínios Afeitos', '').split(';')
                dominios = [d.strip() for d in dominios if d.strip()]
                macroareas[macroarea][segmento].extend(dominios)
            
            # Formatar o texto das categorias
            for macroarea, segmentos in macroareas.items():
                aia_categories_text += f"Macroárea: {macroarea}\n"
                
                for segmento, dominios in segmentos.items():
                    aia_categories_text += f"  Segmento: {segmento}\n"
                    
                    if dominios:
                        aia_categories_text += "    Domínios Afeitos:\n"
                        for dominio in dominios:
                            aia_categories_text += f"      - {dominio}\n"
                
                aia_categories_text += "\n"
        
        prompt = f"""
        Com base nas informações do projeto abaixo, sugira as categorias mais apropriadas do AIA (Áreas de Interesse Aplicado):
        
        Título do Projeto: {project.get('titulo', '')}
        Título Público: {project.get('titulo_publico', '')}
        Objetivo: {project.get('objetivo', '')}
        Descrição Pública: {project.get('descricao_publica', '')}
        Tags: {project.get('tags', '')}
        
        {aia_categories_text}
        
        Você deve classificar o projeto escolhendo EXATAMENTE UMA Macroárea e UM Segmento das opções acima.
        Para Domínios Afeitos, você pode selecionar MÚLTIPLOS domínios que sejam relevantes para o projeto, mas apenas do segmento escolhido.
        
        IMPORTANTE: Nesta primeira etapa, NÃO selecione Domínios Afeitos Outros. Isso será feito em uma etapa posterior.
        
        Forneça sua resposta APENAS em formato JSON válido com a seguinte estrutura:
        {{
            "_aia_n1_macroarea": "Nome da Macroárea escolhida",
            "_aia_n2_segmento": "Nome do Segmento escolhido",
            "_aia_n3_dominio_afeito": "Domínio1;Domínio2;Domínio3",
            "confianca": "ALTA, MÉDIA ou BAIXA",
            "justificativa": "Breve explicação da sua classificação (máximo 2 frases)"
        }}
        
        A confiança deve ser:
        - ALTA: quando você tem certeza da classificação
        - MÉDIA: quando a classificação é provável, mas há outras possibilidades
        - BAIXA: quando há pouca informação ou o projeto poderia se encaixar em várias categorias
        
        É MUITO IMPORTANTE que sua resposta seja um JSON válido, pois será processada automaticamente.
        """
        
        return prompt
    
    def _build_prompt_etapa2(self, project, result_etapa1, dominios_afeitos_outros):
        """
        Constrói o prompt para a segunda etapa: seleção de Domínios Afeitos Outros.
        
        Args:
            project: Dicionário com informações do projeto
            result_etapa1: Resultado da primeira etapa (Micro Área, Segmento e Domínio)
            dominios_afeitos_outros: Lista de domínios afeitos outros disponíveis
            
        Returns:
            String com o prompt formatado
        """
        # Formatar a lista de domínios afeitos outros disponíveis
        dominios_outros_text = ""
        if dominios_afeitos_outros:
            dominios_outros_text = "Domínios Afeitos Outros disponíveis (de outros segmentos da mesma microárea):\n"
            for dominio in dominios_afeitos_outros:
                dominios_outros_text += f"  - {dominio}\n"
        else:
            dominios_outros_text = "Não há Domínios Afeitos Outros disponíveis para esta microárea e segmento."
        
        # Extrair informações da primeira etapa
        macroarea = result_etapa1.get("_aia_n1_macroarea", "")
        segmento = result_etapa1.get("_aia_n2_segmento", "")
        dominio_afeito = result_etapa1.get("_aia_n3_dominio_afeito", "")
        
        prompt = f"""
        Com base nas informações do projeto e na classificação já realizada, selecione os Domínios Afeitos Outros mais apropriados.
        
        Título do Projeto: {project.get('titulo', '')}
        Título Público: {project.get('titulo_publico', '')}
        Objetivo: {project.get('objetivo', '')}
        Descrição Pública: {project.get('descricao_publica', '')}
        Tags: {project.get('tags', '')}
        
        Classificação já realizada:
        - Macroárea: {macroarea}
        - Segmento: {segmento}
        - Domínios Afeitos: {dominio_afeito}
        
        {dominios_outros_text}
        
        IMPORTANTE: Os Domínios Afeitos Outros são domínios de outros segmentos da mesma microárea que também são relevantes para o projeto, mas não são do segmento principal escolhido.
        
        Você deve selecionar APENAS domínios da lista fornecida acima. Se não houver domínios relevantes, use o valor "N/A".
        
        Forneça sua resposta APENAS em formato JSON válido com a seguinte estrutura:
        {{
            "_aia_n3_dominio_outro": "DomínioOutro1;DomínioOutro2"
        }}
        
        Use o formato exato dos nomes dos domínios como listados acima, separados por ponto e vírgula (;).
        
        É MUITO IMPORTANTE que sua resposta seja um JSON válido, pois será processada automaticamente.
        """
        
        return prompt
    
    def process_validation(self, suggestion, validation):
        """
        Processa a validação do usuário para uma sugestão da IA.
        
        Args:
            suggestion: Dicionário com as sugestões da IA
            validation: Dicionário com as validações do usuário (aceito/rejeitado)
            
        Returns:
            Dicionário com as categorias finais após validação
        """
        result = {}
        
        # Mapear nomes de campos
        field_mapping = {
            'microarea': '_aia_n1_macroarea',
            'segmento': '_aia_n2_segmento',
            'dominio': '_aia_n3_dominio_afeito',
            'dominio_outro': '_aia_n3_dominio_outro'
        }
        
        # Processar cada categoria
        for ui_field, db_field in field_mapping.items():
            if ui_field in validation and validation[ui_field] == 'accepted':
                # Se a categoria foi aceita, usar a sugestão da IA
                value = suggestion.get(db_field, '')
                
                # Verificar se estamos lidando com dominio_outro e se o valor é vazio ou N/A
                if db_field == '_aia_n3_dominio_outro' and (not value or value.lower() == 'n/a'):
                    value = 'N/A'
                
                result[db_field] = value  # Usar a chave do banco de dados no resultado
            else:
                # Se a categoria foi rejeitada ou não foi validada, usar o valor manual
                # Mapear o campo manual para o campo do banco de dados
                # Verificar se estamos lidando com dominio_outro (que no formulário é dominio_outros)
                manual_field = f'manual_{ui_field}'
                if ui_field == 'dominio_outro':
                    # Tentar com ambos os nomes (singular e plural)
                    if manual_field not in validation:
                        manual_field = 'manual_dominio_outros'  # Tentar com o nome plural
                    
                    manual_value = validation.get(manual_field, '')
                    # Se o valor manual for vazio, usar N/A
                    if not manual_value:
                        manual_value = 'N/A'
                else:
                    manual_value = validation.get(manual_field, '')
                
                result[db_field] = manual_value  # Usar a chave do banco de dados no resultado
        
        return result
