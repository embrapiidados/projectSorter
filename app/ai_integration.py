import openai
import json

class OpenAIClient:
    def __init__(self, api_key):
        self.api_key = api_key
        openai.api_key = api_key
    
    def suggest_categories(self, project, categories_lists):
        """
        Sugere categorias para um projeto usando a API do OpenAI.
        
        Args:
            project: Dicionário com informações do projeto
            categories_lists: Dicionário com as listas de categorias disponíveis
            
        Returns:
            Dicionário com as categorias sugeridas
        """
        if not self.api_key:
            return {
                "error": "Chave da API OpenAI não configurada"
            }
        
        try:
            # Formar o prompt para o OpenAI
            prompt = self._build_prompt(project, categories_lists)
            
            # Chamar a API do ChatGPT
            response = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "Você é um assistente especializado em categorizar projetos de pesquisa e desenvolvimento."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            # Extrair a resposta
            ai_response = response.choices[0].message.content.strip()
            
            # Tentar analisar como JSON
            try:
                return json.loads(ai_response)
            except json.JSONDecodeError:
                # Tentar extrair apenas a parte JSON da resposta
                start_idx = ai_response.find('{')
                end_idx = ai_response.rfind('}') + 1
                
                if start_idx >= 0 and end_idx > 0:
                    json_str = ai_response[start_idx:end_idx]
                    try:
                        return json.loads(json_str)
                    except:
                        pass
                
                # Retornar um objeto vazio se não conseguir extrair como JSON
                return {
                    "tecnologias_habilitadoras": "",
                    "areas_aplicacao": "",
                    "microarea": "",
                    "segmento": "",
                    "dominio": ""
                }
                
        except Exception as e:
            return {
                "error": f"Erro ao chamar OpenAI: {str(e)}"
            }
    
    def _build_prompt(self, project, categories_lists):
        """Constrói o prompt para o OpenAI com os dados do projeto e categorias disponíveis."""
        prompt = f"""
        Com base nas informações do projeto abaixo, sugira as categorias mais apropriadas das listas fornecidas:
        
        Título do Projeto: {project.get('titulo', '')}
        Título Público: {project.get('titulo_publico', '')}
        Objetivo: {project.get('objetivo', '')}
        Descrição Pública: {project.get('descricao_publica', '')}
        Tags: {project.get('tags', '')}
        
        Escolha EXATAMENTE UMA opção para cada categoria a seguir. A opção deve existir nas listas fornecidas.
        
        Categorias disponíveis:
        
        Tecnologias Habilitadoras: {', '.join(categories_lists.get('tecnologias_habilitadoras', []))}
        
        Áreas de Aplicação: {', '.join(categories_lists.get('areas_aplicacao', []))}
        
        Microárea: {', '.join(categories_lists.get('microarea', []))}
        
        Segmento: {', '.join(categories_lists.get('segmento', []))}
        
        Domínio: {', '.join(categories_lists.get('dominio', []))}
        
        Forneça sua resposta APENAS em formato JSON válido com a seguinte estrutura:
        {
            "tecnologias_habilitadoras": "valor sugerido",
            "areas_aplicacao": "valor sugerido",
            "microarea": "valor sugerido",
            "segmento": "valor sugerido",
            "dominio": "valor sugerido"
        }
        
        É MUITO IMPORTANTE que sua resposta seja um JSON válido, pois será processada automaticamente.
        """
        
        return prompt