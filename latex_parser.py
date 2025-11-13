# latex_parser.py
"""
Parser para el formato LaTeX estándar acordado.

Reglas principales (resumidas):
 - Tema (tema) = primera \section{...} encontrada después de \maketitle (si existe).
 - Subtema (subtema) = última \section* / \subsection* / \subsection encontrada antes de cada ejercicio.
 - Cada ejercicio entre:
     %% EXERCISE_START
        ... primer \[ ... \]  --> ENUNCIADO (posible condición INLINE al final, con ", \quad <condición>")
        ... segundo \[ ... \] --> RESPUESTA
     %% EXERCISE_END
 - **NO** se usa la forma comentada "% condition: ..." (ya no existe en el estándar).
 - El parser devuelve los strings interiores de \[ ... \] **sin modificar** (se preserva LaTeX).
"""
import os
import re
from typing import List, Dict, Optional

def listar_tex_files(directorio: str = "Banco") -> List[str]:
    """Devuelve lista de archivos .tex en el directorio dado."""
    if not os.path.exists(directorio):
        return []
    return [f for f in os.listdir(directorio) if f.lower().endswith(".tex")]

# ---------------- utilidades ---------------- #
def _extract_math_blocks(text: str) -> List[str]:
    """Devuelve lista del contenido interior de cada \[ ... \] en el texto (sin delimitadores)."""
    pattern = re.compile(r'\\\[(.*?)\\\]', re.S)
    return [m.group(1).strip() for m in pattern.finditer(text)]

def _clean_condition(text: str) -> str:
    """
    Normaliza la condición extraída:
      - elimina comas/espacios líderes y el token \quad si está al principio.
      - NO modifica el LaTeX interior (conserva \frac, \left, etc.).
    """
    if not text:
        return ""
    s = text.strip()
    # eliminar \quad iniciales o comas precedentes
    s = re.sub(r'^(?:,|\s|\\quad|\\,)+', '', s)
    return s.strip()

# ---------------- función principal ---------------- #
def parsear_latex(path: str) -> List[Dict[str, Optional[str]]]:
    """
    Parsea un archivo .tex con el estándar y devuelve lista de ejercicios con:
      numero, tema, subtema, enunciado, condiciones, respuesta, archivo_origen
    """
    if not os.path.exists(path):
        raise FileNotFoundError(f"No existe el archivo: {path}")

    with open(path, "r", encoding="utf-8") as f:
        contenido = f.read()

    # posición de \maketitle si existe (para detectar la primera sección válida como tema)
    maketitle_pos = contenido.find(r'\maketitle')
    if maketitle_pos == -1:
        maketitle_pos = 0

    # recolectar tokens: secciones/subsecciones y marcadores de ejercicio
    tokens = []
    for m in re.finditer(r'\\section\*?{([^}]*)}', contenido):
        tokens.append({'type': 'section', 'pos': m.start(), 'title': m.group(1).strip()})
    for m in re.finditer(r'\\subsection\*?{([^}]*)}', contenido):
        tokens.append({'type': 'subsection', 'pos': m.start(), 'title': m.group(1).strip()})
    for m in re.finditer(r'%%\s*EXERCISE_START', contenido, flags=re.I):
        tokens.append({'type': 'exercise_start', 'pos': m.start(), 'title': None})
    for m in re.finditer(r'%%\s*EXERCISE_END', contenido, flags=re.I):
        tokens.append({'type': 'exercise_end', 'pos': m.start(), 'title': None})

    tokens.sort(key=lambda x: x['pos'])

    tema = None
    tema_set = False
    current_subtema = None
    ejercicios: List[Dict[str, Optional[str]]] = []

    i = 0
    n_tokens = len(tokens)
    while i < n_tokens:
        tok = tokens[i]
        ttype = tok['type']

        if ttype == 'section':
            # la PRIMERA sección (después de \maketitle) la guardamos como TEMA general
            if (not tema_set) and (tok['pos'] >= maketitle_pos):
                tema = tok['title']
                tema_set = True
            else:
                # posteriores secciones interpretadas como subtema contextual
                current_subtema = tok['title']
            i += 1
            continue

        if ttype == 'subsection':
            current_subtema = tok['title']
            i += 1
            continue

        if ttype == 'exercise_start':
            # buscar exercise_end correspondiente
            j = i + 1
            end_pos = None
            while j < n_tokens:
                if tokens[j]['type'] == 'exercise_end':
                    end_pos = tokens[j]['pos']
                    break
                j += 1
            if end_pos is None:
                end_pos = len(contenido)

            start_pos = tok['pos']
            block_text = contenido[start_pos:end_pos]

            # ---------------- extraer campos ----------------
            # numero: comentario % id: X o patrón "N)" al inicio del bloque
            numero = None
            m_id = re.search(r'%\s*id\s*:\s*([A-Za-z0-9\-\_]+)', block_text, flags=re.I)
            if m_id:
                numero = m_id.group(1).strip()
            else:
                m_num = re.search(r'^\s*([0-9]+)\)', block_text, flags=re.M)
                if m_num:
                    numero = m_num.group(1).strip()

            # Nota: el estándar actual NO usa "% condition: ..." — sólo condiciones inline con ", \quad"
            math_blocks = _extract_math_blocks(block_text)

            enunciado = ""
            condiciones = ""
            respuesta = ""

            if math_blocks:
                math1 = math_blocks[0]  # primer \[...\] -> enunciado (posible inline cond)

                # Detectar condición INLINE: COMA no escapada seguida de \quad
                # regex: (?<!\\),\s*\\quad
                m_inline = re.search(r'(?<!\\),\s*\\quad', math1)
                if m_inline:
                    # dividir: enunciado = parte anterior a la coma no escapada,
                    # condición = lo que sigue al primer \quad subsecuente
                    comma_idx = m_inline.start()
                    quad_idx = math1.find(r'\quad', comma_idx)
                    if quad_idx == -1:
                        quad_idx = math1.rfind(r'\quad')
                    pre = math1[:comma_idx].rstrip()
                    pre = re.sub(r'(?:,|\s)+$', '', pre)  # limpiar comas/trailing spaces del pre
                    post = math1[quad_idx + len(r'\quad'):].strip() if quad_idx != -1 else math1[comma_idx + 1:].strip()
                    enunciado = pre
                    condiciones = _clean_condition(post)
                else:
                    # No hay condición inline --> enunciado completo
                    enunciado = math1
                    condiciones = ""

                # respuesta = segundo \[...\] si existe
                if len(math_blocks) >= 2:
                    respuesta = math_blocks[1]
                else:
                    # fallback: intentar encontrar \textbf{Rpta: } ... \[...\]
                    m_r = re.search(r'\\textbf\{Rpta[:\s]*\}\s*\\\[(.*?)\\\]', block_text, flags=re.S | re.I)
                    if m_r:
                        respuesta = m_r.group(1).strip()
                    else:
                        respuesta = ""
            else:
                # Si no hay \[...\] en bloque, fallback: primera línea no comentada = enunciado
                lines = [ln for ln in block_text.splitlines() if ln.strip() and not ln.strip().startswith('%')]
                enunciado = lines[0].strip() if lines else ""
                condiciones = ""
                respuesta = ""

            ejercicios.append({
                'numero': numero,
                'tema': tema or "",
                'subtema': current_subtema or "",
                'enunciado': enunciado,
                'condiciones': condiciones,
                'respuesta': respuesta,
                'archivo_origen': os.path.basename(path)
            })

            # avanzar índice al token después del exercise_end (si existía)
            if end_pos == len(contenido):
                i = n_tokens
            else:
                i = j + 1
            continue

        i += 1

    return ejercicios

# pequeño CLI para pruebas rápidas
if __name__ == "__main__":
    import argparse, pprint, sys
    parser = argparse.ArgumentParser(description="Parsear archivo .tex (estándar EDO)")
    parser.add_argument("path", nargs="?", help="ruta al archivo .tex (p.ej. Banco/estandar.tex)")
    args = parser.parse_args()
    if not args.path or not os.path.exists(args.path):
        print("Usar: python latex_parser.py Banco/estandar.tex")
        sys.exit(1)
    res = parsear_latex(args.path)
    pprint.pprint(res, width=140)
