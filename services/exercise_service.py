# services/exercise_service.py
from typing import List, Dict, Tuple
from db import repository

def agregar_ejercicios(ejercicios: List[Dict]) -> Tuple[int, int]:
    """
    Agrega una lista de ejercicios a la DB solo si no existen.
    
    Retorna:
        (cantidad_agregados, cantidad_duplicados)
    """
    agregados = 0
    duplicados = 0

    for ej in ejercicios:
        numero = ej.get('numero')
        if not numero:
            # Saltar ejercicios sin número definido
            continue

  #      if repository.exists_ejercicio(numero):
  #          duplicados += 1
  #          continue
        enunciado = ej.get('enunciado', '').strip()
        if not enunciado:
            # Saltar si no hay texto de enunciado
            continue

        if repository.exists_ejercicio_por_enunciado(enunciado):
            duplicados += 1
            continue


        # Insertar en la DB
        repository.create_ejercicio(ej)
        agregados += 1

    return agregados, duplicados


def validar_ejercicio(ej: Dict) -> bool:
    """
    Valida internamente un ejercicio antes de insertarlo:
      - Debe tener número
      - Debe tener enunciado
      - Tema/Subtema opcionales
    Retorna True si válido, False si no.
    """
    if not ej.get('numero'):
        return False
    if not ej.get('enunciado'):
        return False
    # Opcional: más validaciones aquí
    return True


def agregar_ejercicios_con_validacion(ejercicios: List[Dict]) -> Tuple[int, int]:
    """
    Variante que valida antes de agregar.
    Retorna: (agregados, duplicados)
    """
    agregados = 0
    duplicados = 0

    for ej in ejercicios:
        if not validar_ejercicio(ej):
            continue

        numero = ej['numero']
        if repository.exists_ejercicio(numero):
            duplicados += 1
            continue

        repository.create_ejercicio(ej)
        agregados += 1

    return agregados, duplicados
