import pymysql.cursors

def conectar():
    """Establece la conexión con la base de datos."""
    return pymysql.connect(
        host="localhost",
        user="root",
        password="%local_alcafi.%",
        database="iptv",
        cursorclass=pymysql.cursors.DictCursor
    )

class dbase:
    # connector = pymysql.connect(
    #     host="localhost",
    #     user="root",
    #     password="%local_alcafi.%",
    #     database="iptv",
    #     cursorclass=pymysql.cursors.DictCursor
    # )

    def __init__(self):
        self.connector = self.conectar()
        self.stream_mode = self.read("configuration", "*", {"name": "streaming_mode"})[0].get("value")

            
        # self.create("configuration",{"name":"api_token"})

    def conectar(self):
        """Crea una nueva conexión con la base de datos."""
        return pymysql.connect(
            host="localhost",
            user="root",
            password="%local_alcafi.%",
            database="iptv",
            cursorclass=pymysql.cursors.DictCursor
        )

    def create(self, table, data):
        """Inserta un nuevo registro en la tabla especificada."""
        columns = ', '.join(data.keys())
        values = ', '.join(['%s'] * len(data))
        sql = f"INSERT INTO {table} ({columns}) VALUES ({values})"
        with self.connector.cursor() as cursor:
            cursor.execute(sql, tuple(data.values()))
            self.connector.commit()
            return cursor.lastrowid

    def read(self, table, columns='*', conditions=None):
        """Obtiene registros de la tabla especificada con columnas y condiciones opcionales."""
        if isinstance(columns, (list, tuple)):
            columns = ', '.join(columns)  # Convertir lista/tupla a cadena separada por comas
        
        sql = f"SELECT {columns} FROM {table}"
        
        if conditions:
            placeholders = ' AND '.join([f"{col} = %s" for col in conditions.keys()])
            sql += f" WHERE {placeholders}"
        
        with self.connector.cursor() as cursor:
            if conditions:
                cursor.execute(sql, tuple(conditions.values()))
            else:
                cursor.execute(sql)
            return cursor.fetchall()

    def update(self, table, data, conditions):
        """Actualiza registros en la tabla especificada con condiciones dadas."""
        set_clause = ', '.join([f"{col} = %s" for col in data.keys()])
        where_clause = ' AND '.join([f"{col} = %s" for col in conditions.keys()])
        sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
        with self.connector.cursor() as cursor:
            cursor.execute(sql, tuple(data.values()) + tuple(conditions.values()))
            self.connector.commit()
            return cursor.rowcount

    def delete(self, table, conditions):
        """Elimina registros de la tabla especificada con condiciones dadas."""
        where_clause = ' AND '.join([f"{col} = %s" for col in conditions.keys()])
        sql = f"DELETE FROM {table} WHERE {where_clause}"
        with self.connector.cursor() as cursor:
            cursor.execute(sql, tuple(conditions.values()))
            self.connector.commit()
            return cursor.rowcount

    def close(self):
        """Cierra la conexión con la base de datos."""
        self.connector.close()

import telnetlib
import time
import sys, os
import socket
import requests
from datetime import datetime, timedelta

if len(sys.argv) < 3:
    print("Expected telnet port and name")
    print("Try : console_vlc.exe <PORT> <NAME>")
    sys.exit(1)

try:
    port = int(sys.argv[1])
except:
    print("Port must be int")
    sys.exit(1)

try:
    selected_name = str(sys.argv[2])
except:
    print("name must be str")
    sys.exit(1)

if not os.path.exists("logs"):
    os.mkdir("logs")

HOST = "localhost"
PORT = port
PASSWORD = "alcafi-tv-2025"

contador_reinicios = 0
contador_bandera = 0
intentos_play_stop = 0
barra_aumento = True

def estado_de_internet():
    """Verifica si hay conexión a Internet intentando conectarse a un servidor externo."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return "✅ Conexión a Internet disponible"
    except OSError:
        return "❌ No hay conexión a Internet"

def enviar_comando(comando):
    """Conecta a VLC vía Telnet y envía un comando."""
    try:
        tn = telnetlib.Telnet(HOST, PORT)
        tn.read_until(b"Password: ")
        tn.write(PASSWORD.encode("ascii") + b"\n")
        tn.write(comando.encode("ascii") + b"\n")
        tn.write(b"quit\n")  # Cierra la conexión después de enviar el comando
        print(f"Comando enviado: {comando}")
    except Exception as e:
        print("Error al conectar con VLC:", e)

def obtener_estado():
    """Obtiene el estado actual de VLC (playing, paused, stopped)."""
    try:
        tn = telnetlib.Telnet(HOST, PORT)
        tn.read_until(b"Password: ")
        tn.write(PASSWORD.encode("ascii") + b"\n")
        tn.write(b"status\n")
        salida = tn.read_until(b">").decode("ascii")
        tn.close()
        
        # Buscar el estado dentro de la salida
        if "state playing" in salida:
            return "playing", salida
        elif "state paused" in salida:
            return "paused", salida
        elif "state stopped" in salida:
            return "stopped", salida
        else:
            return "unknown", salida
    except Exception as e:
        print("Error al obtener el estado de VLC:", e)
        return "error", str(e)

def convertir_a_minutos_segundos(segundos):
    """Convierte un número de segundos a un formato mm:ss"""
    minutos = segundos // 60
    segundos_restantes = segundos % 60
    return f"{minutos:02}:{segundos_restantes:02}"

def obtener_tiempo_reproduccion():
    """Obtiene el tiempo de reproducción actual de VLC en formato mm:ss."""
    try:
        tn = telnetlib.Telnet(HOST, PORT)
        tn.read_until(b"Password: ")
        tn.write(PASSWORD.encode("ascii") + b"\n")
        tn.write(b"get_time\n")  # Obtener el tiempo de reproducción
        salida = tn.read_until(b">").decode("ascii")
        tn.close()
        # Procesar la salida para obtener los segundos y convertirlos
        tiempo_str = salida.split("\n")[2].strip()  # El valor de tiempo está en la salida
        segundos = int(tiempo_str)  # Convertir la cadena a un entero
        tiempo_formateado = convertir_a_minutos_segundos(segundos)
        return tiempo_formateado
    
    except Exception as e:
        print("Error al obtener el tiempo de reproducción:", e)
        return None


def enviar_correo():
    ""   

def reiniciar_canal(port):
    db =  dbase()
    channels = db.read("channel","*",{"port":port+1000,"program":"VLC"})
    api_token = db.read("configuration", "*", {"name": "api_token"})[0]
                
    if len(channels) < 1:
            print("canal no encontrado")
            return
    
    channel = channels[0]
    id = channel["id"]
    r = requests.post("http://127.0.0.1:5000/apagarCanal",data={"id":id},headers={"Authorization":api_token["value"]})                
    print("El tiempo de reproducción no ha cambiado. Deteniendo y reiniciando...")
    db2 =  dbase()
    api_token2 = db2.read("configuration", "*", {"name": "api_token"})[0]
    r = requests.post("http://127.0.0.1:5000/encenderCanal",data={"id":id},headers={"Authorization":api_token2["value"]})

# Monitoreo en tiempo real
log_file = f"logs/{selected_name}.log"
with open(log_file, "a+", encoding="utf-8") as f:

    # Función de callback para manejar mensajes de Frida y escribir en el archivo de log
    def on_message(message):
        message = str(message)
        ahora = datetime.now()
        try:
            f.seek(0)  # Mueve el puntero al inicio del archivo
            inicio_de_log = f.readline().split("]")[0][1:]
            inicio_de_log_dt = datetime.strptime(inicio_de_log, "%Y-%m-%d %H:%M:%S.%f")
            if (ahora - inicio_de_log_dt > timedelta(days=60)):
                f.truncate(0)
        except:
            pass
        finally:
            f.seek(0, 2)
        
        f.write(f"[{ahora}] {message} \n")  # Escribir en el archivo de log
        if "error" in message.lower():
            f.write(f"[{ahora}] {estado_de_internet()}\n")
        f.flush()  # Asegurarse de que se escriba inmediatamente

    # Variables para monitorear el tiempo de reproducción
    tiempo_reproduccion_anterior = None

    while True:
        estado, mensaje_completo = obtener_estado()
        on_message(mensaje_completo)
        
        if estado in ["stopped", "paused"]:
            print("VLC está detenido. Reproduciendo nuevamente...")
            # enviar_comando("play")  # Reanudar la reproducción
        
        # Obtener y mostrar el tiempo de reproducción en minutos
        tiempo_reproduccion = obtener_tiempo_reproduccion()
        if tiempo_reproduccion is not None:
            print(f"Tiempo de reproducción: {tiempo_reproduccion} minutos.")
            # Si el tiempo no ha cambiado, significa que la reproducción está detenida
            if tiempo_reproduccion_anterior is not None and tiempo_reproduccion == tiempo_reproduccion_anterior:
                contador_bandera += 1
                barra_aumento = False
                print("Barra esta detenida, intentando poner play")
                print(f"Intento : {contador_bandera}")
                # print("El tiempo de reproducción no ha cambiado. Deteniendo y reiniciando...")
                if tiempo_reproduccion != "00:00" and contador_bandera >= 1:
                    enviar_comando("stop")  # Detener la reproducción
                    time.sleep(1.5)  # Esperar un momento antes de volver a reproducir
                    enviar_comando("play")  # Reanudar la reproducción
                    time.sleep(1)
                # tiempo_reproduccion_anterior = "00:00"
            else:
                barra_aumento = True
                contador_bandera = 0
                contador_reinicios = 0
                tiempo_reproduccion_anterior = tiempo_reproduccion

            if contador_bandera > 5:
                barra_aumento = False
                contador_bandera = 0
                #Este contador de reinicios solo se aumenta cuando son seguidos los reinicios, si se puede reproducir se reinicia el contador de reinicios jaja
                contador_reinicios += 1
                print("Maximo de intentos alcanzados reiniciando canal")
                reiniciar_canal()

            if contador_reinicios > 3:
                "Correo se envía cuando se han hecho más de 3 reinicios sin exito de reproducir el contenido"
                enviar_correo()
        
        time.sleep(5)  # Espera 5 segundos antes de volver a verificar




