import frida
import sys,os
from time import sleep
from datetime import datetime,timedelta
import socket

# Verificar que se proporciona un PID como argumento
if len(sys.argv) < 3:
    print("Uso:  console_ffmpeg.exe <PID> <NAME>")
    sys.exit(1)

try:
    selected_pid = int(sys.argv[1])  # Convertir el argumento a entero
    selected_name = str(sys.argv[2])  # Convertir el argumento a entero
except ValueError:
    print("Error: El PID debe ser un número entero.")
    sys.exit(1)

if not os.path.exists("logs"):
    os.mkdir("logs")

def estado_de_internet():
    """Verifica si hay conexión a Internet intentando conectarse a un servidor externo."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return "✅ Conexión a Internet disponible"
    except OSError:
        return "❌ No hay conexión a Internet"

print(f"Adjuntando al proceso con PID {selected_pid}...")

try:
    # Conectar al proceso en ejecución usando el PID
    session = frida.attach(selected_pid)

    # Script Frida para capturar stdout
    script_code = """
    Interceptor.attach(Module.findExportByName("kernel32.dll", "WriteFile"), {
        onEnter: function(args) {
            var buffer = args[1];
            var size = args[2].toInt32();
            if (size > 0) {
                var output = Memory.readUtf8String(buffer, size);
                send("[STDOUT]: " + output);  // Enviar a la función de callback en Python
            }
        }
    });
    """

    # Inyectar el script en Frida
    script = session.create_script(script_code)
    
    # Abrir archivo de log
    log_file = f"{selected_name}.log"
    with open(log_file,"a+",encoding="utf-8") as f:

        # Función de callback para manejar mensajes de Frida y escribir en el archivo de log
        def on_message(message,data=""):
            ahora = datetime.now()
            try:
                f.seek(0)  # Mueve el puntero al inicio del archivo
                inicio_de_log = f.readline().split("]")[0][1:]
                inicio_de_log_dt = datetime.strptime(inicio_de_log, "%Y-%m-%d %H:%M:%S.%f") 
                if(ahora - inicio_de_log_dt > timedelta(days=60)):
                    f.truncate(0)
            except:
                pass
            finally:
                f.seek(0,2)
            print(message)
            if(message.get("payload") is None and message.get("description") is None):
                return
            if message.get("type") == "error":
                f.write(f"[{ahora}] "+message["description"] + "\n")  # Escribir en el archivo de log
                sleep(4)
            else:
                f.write(f"[{ahora}] "+message["payload"] + "\n")  # Escribir en el archivo de log

            f.flush()  # Asegurarse de que se escriba inmediatamente

        # Establecer la función de callback para manejar mensajes
        script.on("message", on_message)
        # Cargar el script y comenzar a escuchar
        script.load()

        print(f"Capturando salida en tiempo real... Se está escribiendo en {log_file}")
        sys.stdin.read()  # Mantener ejecución

except frida.ProcessNotFoundError:
    print(f"Error: No se pudo encontrar un proceso con PID {selected_pid}.")
    sys.exit(1)
except frida.PermissionDeniedError:
    print("Error: No tienes permisos para adjuntarte a este proceso. Ejecuta con permisos elevados.")
    sys.exit(1)
except Exception as e:
    print(f"Error inesperado: {e}")
    sys.exit(1)
