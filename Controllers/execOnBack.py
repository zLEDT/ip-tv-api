import sys
import subprocess

def ejecutar_archivo():
    if len(sys.argv) < 2:
        print("Por favor, proporciona el archivo a ejecutar y sus parámetros.")
        sys.exit(1)

    # El primer argumento es el nombre del archivo que se va a ejecutar
    archivo = sys.argv[1]

    # Los parámetros adicionales a pasar al archivo
    parametros = sys.argv[2:]

    # Ejecutar el archivo con los parámetros usando subprocess
    try:
        # Esto ejecuta el archivo con los parámetros proporcionados
        resultado = subprocess.run([archivo] + parametros, capture_output=True, text=True,shell=False,creationflags=subprocess.CREATE_NO_WINDOW )

        # Imprimir la salida del proceso
        print("Salida del proceso:")
        print(resultado.stdout)

        # Imprimir los errores si los hay
        if resultado.stderr:
            print("Errores:")
            print(resultado.stderr)

    except FileNotFoundError:
        print(f"Error: El archivo '{archivo}' no se encuentra.")
    except Exception as e:
        print(f"Error al ejecutar el archivo: {e}")

if __name__ == "__main__":
    ejecutar_archivo()
