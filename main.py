import os 
import sys
import time
from rich.table import Table
from rich.console import Console
from latex_parser import listar_tex_files, parsear_latex  # ⚡ import correcto

console = Console()

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def show_title():
    print("=" * 120)
    print("  🐍✨ EDO TITANS - GESTOR DE PRÁCTICAS ✨🐍".center(120))
    print("=" * 120)

def show_menu():
    print("\n¿Qué quieres hacer hoy?\n")
    print("1) 📥 Cargar ejercicios desde LaTeX (simulación, sin DB)")
    print("2) 🛠️ CRUD de ejercicios en la DB")
    print("3) 🎲 Generar práctica aleatoria")
    print("4) 📜 Ver historial de semestres")
    print("5) 🚪 Salir\n")

def mostrar_tabla(ejercicios):
    """
    Muestra los ejercicios en consola en una tabla con colores.
    """
    table = Table(title="📚 Ejercicios Leídos")

    # Columnas
    table.add_column("N°", justify="center", style="cyan", no_wrap=True)
    table.add_column("Sección", style="magenta")
    table.add_column("Subsección", style="magenta")
    table.add_column("Enunciado", style="green")
    table.add_column("Condiciones", style="red")
    table.add_column("Respuesta", style="yellow")
    table.add_column("Archivo", style="blue")

    # Filas
    for i, ej in enumerate(ejercicios, start=1):
        enunciado_line = ej['enunciado'].replace("\n", " ")
        respuesta_line = ej['respuesta'].replace("\n", " ")
        condiciones_line = ej['condiciones'].replace("\n", " ") if ej.get('condiciones') else "-"

        table.add_row(
            str(i),
            ej['seccion'],
            ej.get('subseccion', "-"),
            enunciado_line,
            condiciones_line,
            respuesta_line,
            ej['archivo_origen']
        )

    # Imprimir tabla
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

    # Preguntar si guardar
    decision = input("\n¿Deseas guardar estos ejercicios en la DB? (s/n): ").strip().lower()
    if decision == "s":
        print("\n[+] Guardado en DB (simulado por ahora).")
    else:
        print("\n[-] Operación cancelada, no se guardó nada.")

    input("\nPresiona ENTER para volver al menú...")

    #print("\n[⚡] Nota: en este modo no guardamos nada en DB todavía.")
    #input("\nPresiona ENTER para volver al menú...")

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
