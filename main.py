import os
import sys
import time
from rich.table import Table
from rich.console import Console
from rich.text import Text
from latex_parser import listar_tex_files, parsear_latex

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_title():
    print("=" * 120)
    print("  🐍✨ EDO VILLE - GESTOR DE PRÁCTICAS ✨🐍".center(120))
    print("=" * 120)

def show_menu():
    print("\n¿Qué quieres hacer hoy?\n")
    print("1) 📥 Cargar ejercicios desde LaTeX a la DB")
    print("2) 🛠️ CRUD de ejercicios en la DB")
    print("3) 🎲 Generar práctica aleatoria")
    print("4) 📜 Ver historial de semestres")
    print("5) 🚪 Salir\n")

def mostrar_tabla(ejercicios):
    table = Table(title="📚 Ejercicios Leídos (vista completa)")

    # Columnas
    table.add_column("N°", justify="center", style="cyan", no_wrap=True)
    table.add_column("Tema", style="magenta")
    table.add_column("SubTema", style="magenta")
    table.add_column("Enunciado", style="green")
    table.add_column("Condiciones", style="red")
    table.add_column("Respuesta", style="yellow")
    table.add_column("Archivo", style="blue")

    for i, ej in enumerate(ejercicios, start=1):
        # Enunciado y respuesta: dejar LaTeX intacto, quitar saltos de línea para mostrar en una línea
        enunciado_raw = ej.get('enunciado') or ""
        enunciado_line = " ".join(enunciado_raw.splitlines()).strip()

        respuesta_raw = ej.get('respuesta') or ""
        respuesta_line = " ".join(respuesta_raw.splitlines()).strip()

        # Condiciones: aceptar tanto str como lista/tupla
        cond_raw = ej.get('condiciones')
        if cond_raw is None:
            condiciones_line = ""
        elif isinstance(cond_raw, (list, tuple)):
            # si el parser devolviera lista de condiciones, unir con '; '
            condiciones_line = "; ".join(str(x).strip() for x in cond_raw if x is not None)
        else:
            # es un string (caso normal): usar tal cual (sin hacer join por caracteres)
            condiciones_line = str(cond_raw).strip()

        # Usar Text para evitar que Rich interprete markup en el contenido (LaTeX)
        enunciado_text = Text(enunciado_line)
        condiciones_text = Text(condiciones_line)
        respuesta_text = Text(respuesta_line)

        table.add_row(
            str(ej.get('numero', i)),
            Text(ej.get('tema') or ""),
            Text(ej.get('subtema') or ""),
            enunciado_text,
            condiciones_text,
            respuesta_text,
            Text(ej.get('archivo_origen') or "")
        )

    console.print(table)


def opcion_cargar_latex():
    clear_screen()
    show_title()
    print("\n📥 Cargar ejercicios desde LaTeX\n")

    archivos = listar_tex_files("Banco")

    if not archivos:
        print("⚠️ No se encontraron archivos .tex en la carpeta 'Banco'.")
        input("\nPresiona ENTER para volver al menú...")
        return

    print("Archivos disponibles:")
    for idx, archivo in enumerate(archivos, start=1):
        print(f"{idx}) {archivo}")
    print("0) Todos los archivos")

    choice = input("\n👉 Selecciona un archivo (número) o 0 para todos: ").strip()

    ejercicios = []
    if choice == "0":
        for archivo in archivos:
            ejercicios.extend(parsear_latex(os.path.join("Banco", archivo)))
    elif choice.isdigit() and 1 <= int(choice) <= len(archivos):
        archivo = archivos[int(choice) - 1]
        ejercicios = parsear_latex(os.path.join("Banco", archivo))
    else:
        print("⚠️ Opción inválida.")
        input("\nPresiona ENTER para volver al menú...")
        return

    # Mostrar tabla
    mostrar_tabla(ejercicios)

    input("\nPresiona ENTER para volver al menú...")

def main():
    while True:
        clear_screen()
        show_title()
        show_menu()

        choice = input("👉 Ingresa una opción (1-5): ").strip()

        if choice == "1":
            opcion_cargar_latex()
        elif choice == "2":
            print("\n[+] Módulo CRUD aún en construcción...")
            input("\nPresiona ENTER para continuar...")
        elif choice == "3":
            print("\n[+] Módulo generador aún en construcción...")
            input("\nPresiona ENTER para continuar...")
        elif choice == "4":
            print("\n[+] Módulo historial aún en construcción...")
            input("\nPresiona ENTER para continuar...")
        elif choice == "5":
            print("\nSaliendo del programa... ¡Nos vemos crack! 👋")
            time.sleep(1)
            sys.exit()
        else:
            print("\n⚠️ Opción inválida, intenta de nuevo.")
            input("\nPresiona ENTER para continuar...")

if __name__ == "__main__":
    main()