# db/repository.py
import sqlite3
from typing import Dict, List, Optional

DB_PATH = "db/EDO_DB.db"

def get_connection():
    """Retorna una conexión a la base de datos SQLite."""
    return sqlite3.connect(DB_PATH)

# ----------------- CREATE ----------------- #
def create_ejercicio(ej: Dict):
    """
    Inserta un ejercicio en la DB.
    ej = {
        'numero': str,
        'tema': str,
        'subtema': str,
        'enunciado': str,
        'condiciones': str,
        'respuesta': str,
        'archivo_origen': str
    }
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("""
        INSERT INTO ejercicios(numero, tema, subtema, enunciado, condiciones, respuesta, archivo_origen)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    """, (
        ej.get('numero'),
        ej.get('tema'),
        ej.get('subtema'),
        ej.get('enunciado'),
        ej.get('condiciones'),
        ej.get('respuesta'),
        ej.get('archivo_origen')
    ))
    conn.commit()
    conn.close()

# ----------------- READ ----------------- #
def read_ejercicios(filtros: Optional[Dict[str,str]] = None) -> List[Dict]:
    """
    Devuelve la lista de ejercicios.
    filtros: dict opcional con columnas y valores para filtrar.
    """
    conn = get_connection()
    c = conn.cursor()

    query = "SELECT numero, enunciado, condiciones, respuesta, tema, subtema, archivo_origen FROM ejercicios"
    params = []

    if filtros:
        condiciones = []
        for k, v in filtros.items():
            condiciones.append(f"{k} = ?")
            params.append(v)
        query += " WHERE " + " AND ".join(condiciones)

    c.execute(query, params)
    rows = c.fetchall()
    conn.close()

    # mapeo corregido: r[0]=numero, r[1]=enunciado, r[2]=condiciones, r[3]=respuesta, r[4]=tema, r[5]=subtema, r[6]=archivo_origen
    return [
        {
            'numero': r[0],
            'enunciado': r[1],
            'condiciones': r[2],
            'respuesta': r[3],
            'tema': r[4],
            'subtema': r[5],
            'archivo_origen': r[6]
        } for r in rows
    ]

# ----------------- EXISTENCE ----------------- #
def exists_ejercicio(numero: str) -> bool:
    """
    Retorna True si ya existe un ejercicio con ese número.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT 1 FROM ejercicios WHERE numero = ?", (numero,))
    res = c.fetchone()
    conn.close()
    return res is not None

def exists_ejercicio_por_enunciado(enunciado: str) -> bool:
    """
    Retorna True si ya existe un ejercicio con el mismo enunciado (texto exacto).
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("SELECT 1 FROM ejercicios WHERE TRIM(enunciado) = TRIM(?)", (enunciado,))
    res = c.fetchone()
    conn.close()
    return res is not None


# ----------------- UPDATE ----------------- #
def update_ejercicio(numero: str, cambios: Dict):
    """
    Actualiza un ejercicio por su número.
    cambios: dict con columnas y nuevos valores.
    """
    if not cambios:
        return
    conn = get_connection()
    c = conn.cursor()
    sets = ", ".join([f"{k} = ?" for k in cambios.keys()])
    c.execute(f"UPDATE ejercicios SET {sets} WHERE numero = ?", (*cambios.values(), numero))
    conn.commit()
    conn.close()

# ----------------- DELETE ----------------- #
def delete_ejercicio(numero: str):
    """
    Elimina un ejercicio por su número.
    """
    conn = get_connection()
    c = conn.cursor()
    c.execute("DELETE FROM ejercicios WHERE numero = ?", (numero,))
    conn.commit()
    conn.close()
