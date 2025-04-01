import pandas as pd
import io

class ExcelManager:
    @staticmethod
    def read_projects(file_content):
        """Lê a aba de projetos do arquivo Excel."""
        try:
            excel_file = io.BytesIO(file_content)
            df = pd.read_excel(excel_file, sheet_name='projetos')
            return df.to_dict('records')
        except Exception as e:
            raise Exception(f"Erro ao ler projetos: {str(e)}")
    
    @staticmethod
    def read_categories(file_content):
        """Lê a aba de categorias do arquivo Excel."""
        try:
            excel_file = io.BytesIO(file_content)
            df = pd.read_excel(excel_file, sheet_name='categorias')
            return df.to_dict('records')
        except Exception as e:
            raise Exception(f"Erro ao ler categorias: {str(e)}")
    
    @staticmethod
    def read_categories_lists(file_content):
        """Lê a aba de listas de categorias do arquivo Excel."""
        try:
            excel_file = io.BytesIO(file_content)
            df = pd.read_excel(excel_file, sheet_name='categorias_lists')
            
            # Organizar os dados em dicionários por coluna
            result = {}
            for column in df.columns:
                # Remover valores nulos ou vazios
                values = df[column].dropna().tolist()
                # Remover valores vazios (strings)
                values = [v for v in values if str(v).strip()]
                result[column] = values
                
            return result
        except Exception as e:
            raise Exception(f"Erro ao ler listas de categorias: {str(e)}")
    
    @staticmethod
    def update_category(file_content, category_data):
        """Atualiza ou adiciona uma categorização de projeto."""
        try:
            # Carregar todas as abas do Excel
            excel_file = io.BytesIO(file_content)
            writer = pd.ExcelWriter(io.BytesIO(), engine='openpyxl')
            
            for sheet_name in ['projetos', 'categorias', 'categorias_lists']:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                if sheet_name == 'categorias':
                    # Verificar se o projeto já existe na aba de categorias
                    idx = df[df['id_projeto'] == category_data['id_projeto']].index
                    
                    if len(idx) > 0:
                        # Atualizar registro existente
                        for key, value in category_data.items():
                            df.loc[idx[0], key] = value
                    else:
                        # Adicionar novo registro
                        df = pd.concat([df, pd.DataFrame([category_data])], ignore_index=True)
                
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Obter o conteúdo atualizado
            writer.save()
            updated_content = writer.bookwriter.getvalue()
            
            return updated_content
        except Exception as e:
            raise Exception(f"Erro ao atualizar categoria: {str(e)}")
    
    @staticmethod
    def update_categories_lists(file_content, lists_data):
        """Atualiza as listas de categorias."""
        try:
            # Carregar todas as abas do Excel
            excel_file = io.BytesIO(file_content)
            writer = pd.ExcelWriter(io.BytesIO(), engine='openpyxl')
            
            for sheet_name in ['projetos', 'categorias', 'categorias_lists']:
                df = pd.read_excel(excel_file, sheet_name=sheet_name)
                
                if sheet_name == 'categorias_lists':
                    # Criar um novo DataFrame com os dados atualizados
                    max_length = max(len(values) for values in lists_data.values())
                    new_data = {}
                    
                    for column, values in lists_data.items():
                        # Preencher com NaN para manter o mesmo comprimento
                        padded_values = values + [None] * (max_length - len(values))
                        new_data[column] = padded_values
                    
                    df = pd.DataFrame(new_data)
                
                df.to_excel(writer, sheet_name=sheet_name, index=False)
            
            # Obter o conteúdo atualizado
            writer.save()
            updated_content = writer.bookwriter.getvalue()
            
            return updated_content
        except Exception as e:
            raise Exception(f"Erro ao atualizar listas de categorias: {str(e)}")