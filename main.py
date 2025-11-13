import os
import sys
import time
from rich.table import Table
from rich.console import Console
from rich.panel import Panel
from rich.prompt import Prompt
from pyfiglet import Figlet

from latex_parser import listar_tex_files, parsear_latex
from services.exercise_service import agregar_ejercicios
from db import repository  # para leer y filtrar ejercicios de la DB

console = Console()


# ------------------ UTILIDADES ------------------ #
def clear_screen():
    """Limpia la consola según el sistema operativo."""
    os.system('cls' if os.name == 'nt' else 'clear')


def show_title():
    """
    Muestra el título principal del programa con estilo ASCII (usando pyfiglet)
    y dentro de un panel decorativo de la librería 'rich'.
    """
    f = Figlet(font="slant")  # Fuente en estilo “slant”, hay muchas más (doom, banner, etc.)
    banner = f.renderText("EDO - USFX")

    # Panel.fit adapta el tamaño al texto. El 'style' define color de texto y fondo.
    console.print(Panel.fit(
        banner,
        title="🐍✨ Gestor de Prácticas ✨🐍",
        style="bold white on black"
    ))


def hacker_typing(text, delay=0.01, color="cyan"):
    """
    Imita el efecto de escritura “hacker”, imprimiendo letra por letra con retardo.
    Parámetros:
        - text: texto a mostrar
        - delay: retardo entre caracteres
        - color: color del texto (cyan, green, red, etc.)
    """
    for char in text:
        console.print(char, end="", style=color)
        sys.stdout.flush()
        time.sleep(delay)
    console.print()  # Salto de línea al final


def mostrar_tabla(ejercicios):
    """
    Muestra una tabla con los ejercicios usando la librería 'rich'.
    Cada columna tiene su propio color para diferenciar campos.
    """
    table = Table(title="📚 Ejercicios", style="bold cyan")

    # Definición de columnas con sus estilos
    columnas = [
        ("N°", "center", "cyan"),
        ("Tema", None, "magenta"),
        ("SubTema", None, "magenta"),
        ("Enunciado", None, "green"),
        ("Condiciones", None, "red"),
        ("Respuesta", None, "yellow"),
        ("Archivo", None, "blue")
    ]

    # Se agregan las columnas usando un bucle limpio
    for titulo, align, color in columnas:
        table.add_column(titulo, justify=align, style=color, no_wrap=True if align else False)

    # Se agregan las filas con los datos
    for i, ej in enumerate(ejercicios, start=1):
        enunciado = " ".join((ej.get('enunciado') or "").splitlines()).strip()
        respuesta = " ".join((ej.get('respuesta') or "").splitlines()).strip()
        condiciones = ej.get('condiciones')

        # Normalización de condiciones (list, tuple o string)
        if isinstance(condiciones, (list, tuple)):
            condiciones_str = "; ".join(str(c).strip() for c in condiciones if c)
        else:
            condiciones_str = str(condiciones or "").strip()

        table.add_row(
            str(ej.get('numero', i)),
            ej.get('tema', ""),
            ej.get('subtema', ""),
            enunciado,
            condiciones_str,
            respuesta,
            ej.get('archivo_origen', "")
        )

    console.print(table)



# ------------------ MENÚ PRINCIPAL ------------------ #
def show_menu():
    """Muestra las opciones del menú principal con colores e íconos."""
    console.print("\n[bold magenta]>>> ¿Qué querés hacer hoy? <<<[/bold magenta]\n")

    # Lista de tuplas con (opción, descripción, color)
    menu_items = [
        ("1", "📥 Cargar y agregar ejercicios desde un Archivo .Tex a la DB", "red"),
        ("2", "📂 Consultar / Editar / Borrar ejercicios en la DB", "yellow"),
        ("3", "🎲 Generar práctica aleatoria", "green"),
        ("4", "📜 Ver historial de semestres", "magenta"),
        ("5", "🚪 Salir", "blue"),
    ]

    # Mostrar opciones con formato de color
    for key, text, color in menu_items:
        console.print(f"[{color}]{key}) {text}[/{color}]")


# ------------------ OPCIÓN 1: CARGAR LATEX ------------------ #
def opcion_cargar_latex():
    clear_screen()
    show_title()
    hacker_typing("\n📥 Escaneando archivos .tex...\n", delay=0.02, color="green")

    archivos = listar_tex_files("data")
    if not archivos:
        console.print("[bold red]⚠️ No se encontraron archivos .tex en la carpeta 'Banco'.[/bold red]")
        input("\nPresiona ENTER para volver al menú...")
        return

    # Mostrar archivos disponibles
    for i, archivo in enumerate(archivos, start=1):
        console.print(f"[cyan]{i})[/cyan] {archivo}")
    console.print("[yellow]0) Todos los archivos[/yellow]")

    choice = Prompt.ask("\n👉 Selecciona un archivo", choices=[str(i) for i in range(len(archivos) + 1)])
    ejercicios = []

    # Si elige “0” se procesan todos los archivos
    if choice == "0":
        for archivo in archivos:
            ejercicios.extend(parsear_latex(os.path.join("data", archivo)))
    else:
        seleccionado = archivos[int(choice) - 1]
        ejercicios = parsear_latex(os.path.join("data", seleccionado))

    mostrar_tabla(ejercicios)

    # Confirmación antes de agregar a la base de datos
    if ejercicios and Prompt.ask("\n¿Deseas agregar estos ejercicios a la DB?", choices=["s", "n"]) == "s":
        agregados, duplicados = agregar_ejercicios(ejercicios)
        console.print(f"[green]✅ {agregados} ejercicios agregados[/green]")
        if duplicados:
            console.print(f"[yellow]⚠️ {duplicados} ejercicios ya existían y no se agregaron[/yellow]")

    input("\nPresiona ENTER para volver al menú...")


# ------------------ OPCIÓN 2: CONSULTAR / CRUD ------------------ #
def opcion_crud_db():
    while True:
        clear_screen()
        show_title()
        console.print("\n[bold yellow]>>> Consultar / Editar / Borrar <<<[/bold yellow]\n")

        opciones = {
            "1": "Ver todos los ejercicios",
            "2": "Buscar por tema/subtema",
            "3": "Editar ejercicio (pendiente)",
            "4": "Eliminar ejercicio (pendiente)",
            "5": "Volver al menú principal"
        }

        for key, value in opciones.items():
            console.print(f"[cyan]{key}[/cyan]) {value}")

        choice = Prompt.ask("\n👉 Selecciona una opción", choices=opciones.keys())

        if choice == "1":
            ejercicios = repository.read_ejercicios()
            mostrar_tabla(ejercicios)
        elif choice == "2":
            tema = Prompt.ask("📌 Ingresa el tema (dejar vacío para omitir)", default="")
            subtema = Prompt.ask("📌 Ingresa el subtema (dejar vacío para omitir)", default="")
            filtros = {k: v for k, v in {"tema": tema, "subtema": subtema}.items() if v}
            ejercicios = repository.read_ejercicios(filtros=filtros)
            mostrar_tabla(ejercicios)
        elif choice in ["3", "4"]:
            console.print("[yellow]Función aún no implementada[/yellow]")
        elif choice == "5":
            break

        input("\nPresiona ENTER para volver...")


# ------------------ MAIN ------------------ #
def main():
    """Control principal del programa."""
    while True:
        clear_screen()
        show_title()
        show_menu()

        opciones = {
            "1": opcion_cargar_latex,
            "2": opcion_crud_db,
            "3": lambda: console.print("\n[green][+] Módulo generador aún en construcción...[/green]"),
            "4": lambda: console.print("\n[magenta][+] Módulo historial aún en construcción...[/magenta]"),
            "5": "salir",
        }

        choice = Prompt.ask("\n👉 Ingresá una opción", choices=opciones.keys())

        if choice == "5":
            hacker_typing("\nSaliendo del programa... ¡Nos vemos crack! 👋", delay=0.02, color="red")
            time.sleep(1)
            sys.exit()
        else:
            # Ejecutar la función asociada a la opción
            accion = opciones[choice]
            if callable(accion):
                accion()
            input("\nPresiona ENTER para continuar...")


if __name__ == "__main__":
    main()
