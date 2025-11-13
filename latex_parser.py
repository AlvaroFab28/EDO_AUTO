import os

def listar_tex_files(directorio="Banco"):
    """Devuelve una lista de archivos .tex en el directorio dado."""
    if not os.path.exists(directorio):
        return []
    return [f for f in os.listdir(directorio) if f.endswith(".tex")]

def parsear_latex(path):
    """
    Simulación de parser: debería leer .tex real,
    pero por ahora devolvemos datos ficticios.
    """
    return [
        {
            "numero": 1,
            "enunciado": "y' + y = e^x",
            "respuesta": "y = Ce^{-x} + e^x",
            "seccion": "2.1) Variable separable",
            "archivo_origen": os.path.basename(path)
        },
        {
            "numero": 2,
            "enunciado": "y'' - y = 0",
            "respuesta": "y = C1 e^x + C2 e^{-x}",
            "seccion": "2.2) Ecuación lineal homogénea",
            "archivo_origen": os.path.basename(path)
        }
    ]
