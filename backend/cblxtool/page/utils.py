import os
import html
from pathlib import Path
from django.conf import settings
from typing import Dict, List, Any

def _nl2br(s: str) -> str:
    return (s or '').replace('\r\n', '\n').replace('\r', '\n').replace('\n', '<br>')

def _esc(s: Any) -> str:
    return html.escape(str(s) if s is not None else '')
    
def salvar_html_fisico(email: str, projeto_nome: str, fase: str, numero_pagina: int, conteudo: Any) -> str:
    """
    Salva conteúdo como arquivo HTML físico no sistema de arquivos.
    """
    # Validação de parâmetros
    if not all([email, projeto_nome, fase]):
        raise ValueError("Email, projeto_nome e fase são obrigatórios")
    
    if numero_pagina < 1:
        raise ValueError("Número da página deve ser maior que 0")
    
    # Sanitiza nomes
    email_sanitizado = email.replace('/', '_').replace('\\', '_')
    projeto_sanitizado = projeto_nome.replace('/', '_').replace('\\', '_')
    fase_sanitizada = fase.replace('/', '_').replace('\\', '_')
    
    # Cria diretórios
    base_path = Path(settings.BASE_DIR) / 'media' / 'user' / email_sanitizado / 'content' / 'Projects' / projeto_sanitizado / fase_sanitizada
    base_path.mkdir(parents=True, exist_ok=True)
    
    nome_arquivo = f"pagina{numero_pagina}.html"
    caminho_arquivo = base_path / nome_arquivo
    
    # Constrói o corpo HTML
    html_corpo = ""

    if isinstance(conteudo, dict):
        # ✅ Página 1 (steps): big_idea / essential_question / challenge
        for chave, blocos in conteudo.items():
            if chave in ['big_idea', 'essential_question', 'challenge']:
                titulo_secao = _esc(chave.replace('_', ' ').title())
                html_corpo += f"        <h2>{titulo_secao}</h2>\n"
                
                if isinstance(blocos, list):
                    for bloco in blocos:
                        if isinstance(bloco, dict):
                            content = _esc(bloco.get('content', ''))
                        else:
                            content = _esc(bloco)
                        if content.strip():
                            html_corpo += f"        <p>{_nl2br(content)}</p>\n"
                elif blocos:  # Handle non-list content
                    html_corpo += f"        <p>{_nl2br(_esc(blocos))}</p>\n"

    elif isinstance(conteudo, list):
        # ✅ Páginas 2–5 (blocks)
        for bloco in conteudo:
            if not isinstance(bloco, dict):
                continue

            btype = bloco.get('type')
            data = bloco.get('data')

            if btype == 'text':
                # Handle text content
                if isinstance(data, dict):
                    text = _esc(data.get('text', ''))
                else:
                    text = _esc(data)
                if text.strip():
                    html_corpo += f"        <p>{_nl2br(text)}</p>\n"

            elif btype == 'image':
                # Handle image content
                url = ''
                if isinstance(data, dict):
                    url = _esc(data.get('imageUrl', ''))
                if url:
                    html_corpo += f'        <p><img src="{url}" alt="" style="max-width:100%"></p>\n'

            elif btype == 'table':
                # Handle table content
                rows = []
                if isinstance(data, dict):
                    rows = data.get('rows') or []
                if isinstance(rows, list) and rows:
                    trs = []
                    for r in rows:
                        if not isinstance(r, list): 
                            continue
                        tds = ''.join(f'<td>{_esc(c)}</td>' for c in r)
                        trs.append(f'<tr>{tds}</tr>')
                    html_corpo += f'        <table border="1" cellspacing="0" cellpadding="6">\n          {"".join(trs)}\n        </table>\n'

            elif btype == 'file':
                # Handle file content
                file_name = 'Arquivo'
                file_path = '#'
                if isinstance(data, dict):
                    file_name = _esc(data.get('fileName', 'Arquivo'))
                    file_path = _esc(data.get('filePath', '#'))
                html_corpo += f'        <p><a href="{file_path}" target="_blank" rel="noopener">{file_name}</a></p>\n'

    # If no content was generated, add a placeholder
    if not html_corpo.strip():
        html_corpo = "        <p>Conteúdo da página será exibido aqui.</p>\n"

    # HTML template
    titulo_pagina = _esc(f"{fase} - Página {numero_pagina}")
    html_completo = f"""<!DOCTYPE html>
<html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>{titulo_pagina}</title>
        <style>
            body {{
                font-family: Arial, sans-serif;
                line-height: 1.6;
                margin: 0;
                padding: 20px;
                background-color: #f4f4f4;
            }}
            .container {{
                max-width: 800px;
                margin: 0 auto;
                background: white;
                padding: 20px;
                border-radius: 8px;
                box-shadow: 0 0 10px rgba(0,0,0,0.1);
            }}
            h1 {{
                color: #333;
                border-bottom: 2px solid #007bff;
                padding-bottom: 10px;
            }}
            h2 {{
                color: #555;
                margin-top: 30px;
            }}
            p {{
                text-align: justify;
                margin-bottom: 15px;
            }}
            table {{
                margin: 16px 0;
                width: 100%;
                border-collapse: collapse;
            }}
            td {{
                border: 1px solid #ccc;
                padding: 6px 8px;
            }}
            img {{
                max-width: 100%;
                height: auto;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <h1>{titulo_pagina}</h1>
{html_corpo}        </div>
    </body>
</html>"""

    try:
        with open(caminho_arquivo, "w", encoding="utf-8") as f:
            f.write(html_completo)
        return str(caminho_arquivo)
    except OSError as e:
        raise OSError(f"Erro ao salvar arquivo HTML: {e}")
    
# Versão alternativa usando apenas as correções essenciais (mais próxima do original)
def salvar_html_fisico_simples(email: str, projeto_nome: str, fase: str, numero_pagina: int, conteudo: dict):
    """Versão simplificada com apenas as correções essenciais"""
    # Monta caminho: BASE_DIR / media / user / {email} / content / Projects / {projeto} / {fase}
    base_path = os.path.join(
        settings.BASE_DIR,
        'media',
        'user',
        email,
        'content',
        'Projects',
        projeto_nome,
        fase
    )
    os.makedirs(base_path, exist_ok=True)

    nome_arquivo = f"pagina{numero_pagina}.html"
    caminho_arquivo = os.path.join(base_path, nome_arquivo)

    html_corpo = ""
    if isinstance(conteudo, dict):
        for chave, blocos in conteudo.items():
            html_corpo += f"<h2>{chave.replace('_', ' ').title()}</h2>\n"
            for bloco in blocos:
                # Verifica se é dict antes de usar .get()
                if isinstance(bloco, dict):
                    content = bloco.get('content', '')
                else:
                    content = str(bloco)
                html_corpo += f"<p>{content}</p>\n"
    elif isinstance(conteudo, list):
        for bloco in conteudo:
            if isinstance(bloco, dict) and bloco.get('type') == 'text':
                content = bloco.get('data', '')
                html_corpo += f"<p>{content}</p>\n"
    # HTML com indentação correta
    html_completo = f"""<!DOCTYPE html>
<html lang="pt-BR">
    <head>
        <meta charset="UTF-8">
        <title>{fase} - Página {numero_pagina}</title>
    </head>
    <body>
        <h1>{fase} - Página {numero_pagina}</h1>
        {html_corpo}
    </body>
</html>"""

    with open(caminho_arquivo, "w", encoding="utf-8") as f:
        f.write(html_completo)
