from PIL import Image, ImageDraw
import os

def create_favicon():
    """
    Cria um favicon simples para a aplicação.
    Requer a biblioteca Pillow (PIL).
    """
    # Garantir que o diretório existe
    static_dir = os.path.join('app', 'static')
    os.makedirs(static_dir, exist_ok=True)
    
    # Caminho do arquivo favicon
    favicon_path = os.path.join(static_dir, 'favicon.ico')
    
    # Criar imagem
    img = Image.new('RGBA', (64, 64), color=(0, 0, 0, 0))
    draw = ImageDraw.Draw(img)
    
    # Desenhar um fundo azul (cor Bootstrap primary)
    draw.rectangle([(0, 0), (64, 64)], fill=(13, 110, 253))
    
    # Desenhar um "C" branco estilizado
    draw.arc([(10, 10), (54, 54)], start=45, end=315, fill=(255, 255, 255), width=8)
    
    # Adicionar uma linha horizontal para simbolizar "categorização"
    draw.line([(32, 25), (32, 45)], fill=(255, 255, 255), width=6)
    
    # Salvar o favicon
    img.save(favicon_path)
    print(f"Favicon criado em {favicon_path}")

if __name__ == "__main__":
    try:
        create_favicon()
    except Exception as e:
        print(f"Erro ao criar favicon: {e}")
        print("Por favor, instale a biblioteca Pillow: pip install pillow")