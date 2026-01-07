from pathlib import Path
ABSOLUTE_PATH =  str(Path(__file__).parent.parent)

if __name__ == "__main__":
    import sys
    sys.path.append(ABSOLUTE_PATH)  # Agregando el area de trabajo al path 

from Database.database import dbase
import subprocess

def validate(condition_to_search={"id": "2"}):
    """Función para verificar si existe un registro en la tabla 'channel' con la condición dada."""
    db = dbase()
    result = db.read("channel", condition_to_search)
    db.close()
    return len(result) > 0  # Devuelve True si existe el registro, False si no existe

def check_status(pid,target="vlc"):
    """
    Verifica si un proceso con el PID dado está en ejecución en Windows.
    
    :param pid: Identificador del proceso (PID).
    :return: True si el proceso está en ejecución, False en caso contrario.
    """
    print(pid)
    command = f'tasklist /FI "PID eq {pid}"'
    output = subprocess.run(command, shell=True, capture_output=True, text=True).stdout
    lines =output.splitlines() 
    if len(lines) > 2:
        # print(output.find("vlc"))
        # print("EJECUTE :",output[output.find("vlc")-8:output.find("vlc")+7])
        #Validamos si no es consola de vlc 
        vlc_name = output[output.find("vlc")-8:output.find("vlc")+7]
        
        if not target in output:
            return False
         
        if not ("vlc" in output) and not ("obs" in output):
            return False
        
        if "console_vlc" in vlc_name:
            return False
        
        if "obs-browser" in output:
            return False

    # Si la salida tiene más de 2 líneas, significa que el proceso existe
    return len(output.splitlines()) > 2

# # Ejemplo de uso
# pid = 21628  # Reemplaza con un PID real
# if check_status(pid):
#     print(f"El proceso con PID {pid} está en ejecución.")
# else:
#     print(f"El proceso con PID {pid} no está en ejecución.")
