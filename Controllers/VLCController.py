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

# class dbase:
#     # connector = pymysql.connect(
#     #     host="localhost",
#     #     user="root",
#     #     password="%local_alcafi.%",
#     #     database="iptv",
#     #     cursorclass=pymysql.cursors.DictCursor
#     # )

#     def __init__(self):
#         self.connector = self.conectar()
#         self.stream_mode = self.read("configuration", "*", {"name": "streaming_mode"})[0].get("value")

            
#         # self.create("configuration",{"name":"api_token"})

#     def conectar(self):
#         """Crea una nueva conexión con la base de datos."""
#         return pymysql.connect(
#             host="localhost",
#             user="root",
#             password="",
#             database="ip-tv",
#             cursorclass=pymysql.cursors.DictCursor
#         )

#     def create(self, table, data):
#         """Inserta un nuevo registro en la tabla especificada."""
#         columns = ', '.join(data.keys())
#         values = ', '.join(['%s'] * len(data))
#         sql = f"INSERT INTO {table} ({columns}) VALUES ({values})"
#         with self.connector.cursor() as cursor:
#             cursor.execute(sql, tuple(data.values()))
#             self.connector.commit()
#             return cursor.lastrowid

#     def read(self, table, columns='*', conditions=None):
#         """Obtiene registros de la tabla especificada con columnas y condiciones opcionales."""
#         if isinstance(columns, (list, tuple)):
#             columns = ', '.join(columns)  # Convertir lista/tupla a cadena separada por comas
        
#         sql = f"SELECT {columns} FROM {table}"
        
#         if conditions:
#             placeholders = ' AND '.join([f"{col} = %s" for col in conditions.keys()])
#             sql += f" WHERE {placeholders}"
        
#         with self.connector.cursor() as cursor:
#             if conditions:
#                 cursor.execute(sql, tuple(conditions.values()))
#             else:
#                 cursor.execute(sql)
#             return cursor.fetchall()

#     def update(self, table, data, conditions):
#         """Actualiza registros en la tabla especificada con condiciones dadas."""
#         set_clause = ', '.join([f"{col} = %s" for col in data.keys()])
#         where_clause = ' AND '.join([f"{col} = %s" for col in conditions.keys()])
#         sql = f"UPDATE {table} SET {set_clause} WHERE {where_clause}"
#         with self.connector.cursor() as cursor:
#             cursor.execute(sql, tuple(data.values()) + tuple(conditions.values()))
#             self.connector.commit()
#             return cursor.rowcount

#     def delete(self, table, conditions):
#         """Elimina registros de la tabla especificada con condiciones dadas."""
#         where_clause = ' AND '.join([f"{col} = %s" for col in conditions.keys()])
#         sql = f"DELETE FROM {table} WHERE {where_clause}"
#         with self.connector.cursor() as cursor:
#             cursor.execute(sql, tuple(conditions.values()))
#             self.connector.commit()
#             return cursor.rowcount

#     def close(self):
#         """Cierra la conexión con la base de datos."""
#         self.connector.close()

import telnetlib
import time
import sys, os
import socket
import requests
from datetime import datetime, timedelta
from Controllers.loop import loop
from Librarys.Librarys import *
from Database.database import dbase
if not os.path.exists("logs"):
    os.mkdir("logs")

def estado_de_internet():
    """Verifica si hay conexión a Internet intentando conectarse a un servidor externo."""
    try:
        socket.create_connection(("8.8.8.8", 53), timeout=3)
        return "✅ Conexión a Internet disponible"
    except OSError:
        return "❌ No hay conexión a Internet"

def convertir_a_minutos_segundos(segundos):
    """Convierte un número de segundos a un formato mm:ss"""
    minutos = segundos // 60
    segundos_restantes = segundos % 60
    return f"{minutos:02}:{segundos_restantes:02}"

def enviar_correo():
    ""   


# Monitoreo en tiempo real

class console_vlc:
    HOST = "localhost"
    PASSWORD = "alcafi-tv-2025"

    def __init__(self,port):
        self.port = port
        self.vlc_telnet_port = self.port - 1000
        self.db =  dbase()
        self.status = "stopped"
        self.current_time = 0
        #OBTENCION Y SETEO DE DATOS
        self.getChanneldata()
        self.log_file = f"logs/{self.channelName}.log"



        
        #Variables de bandera
        self.contador_reinicios = 0
        self.contador_bandera = 0
        self.intentos_play_stop = 0
        self.barra_aumento = True

    def getStability(self):
        stability = "stable"

        if self.contador_bandera > 1:
            "CONTADOR BANDERA PARA INDICAR CUANTAS VECES SE HA DETENIDO EL CANAL (VECES SEGUIDAS)"
            stability = "unstable"
            self.on_message(f"Estabilidad de {self.channelName}: {stability}")

        if self.contador_reinicios > 1:
            "CONTADOR REINICIOS PARA INDICAR CUANTAS VECES SE HA REINICIADO EL CANAL (VECES SEGUIDAS)"
            stability = "critical"
            self.on_message(f"Estabilidad de {self.channelName}: {stability}")
        if  self.status  == "offline":
            stability = "offline"

        return stability

    def getChanneldata(self):
        self.channel = self.db.read("channel","*",{"port":self.port,"program":"VLC"})
        self.channel_id = self.channel[0]["id"] if self.channel else None
        self.channelName = self.channel[0]["name"] if self.channel else "Unknown"

    def obtener_estado(self):
        """Obtiene el estado actual de VLC (playing, paused, stopped)."""
        try:
            tn = telnetlib.Telnet(self.HOST, self.vlc_telnet_port)
            tn.read_until(b"Password: ")
            tn.write(self.PASSWORD.encode("ascii") + b"\n")
            tn.write(b"status\n")
            salida = tn.read_until(b">").decode("ascii")
            tn.close()
            
            # Buscar el estado dentro de la salida
            if "state playing" in salida:
                self.status = "playing"
                return "playing", salida
            elif "state paused" in salida:
                self.status = "paused"
                return "paused", salida
            elif "state stopped" in salida:
                self.status = "stopped"
                return "stopped", salida
            else:
                return "unknown", salida
        except Exception as e:
            self.status = "offline"
            # print(f"Error al obtener el estado de canal {self.channelName}:", e)
            self.on_message(f"Error al hacer conexión con el canal {self.channelName}: {e}\nPuede deberse a que VLC no está en ejecución.")
            return "error", str(e)

    @loop
    def iniciar_monitoreo(self):
        "Iniciamos el monitoreo vía consola telnet"
        tiempo_reproduccion_anterior = None
        print("Monitoreo de canal ", self.channelName," iniciado")

        while True:
            estado, mensaje_completo = self.obtener_estado()
            self.on_message(mensaje_completo)
            
            if estado in ["stopped", "paused"]:
                print(f"VLC de {self.channelName} está detenido. Reproduciendo nuevamente...")
                self.enviar_comando("play")  # Reanudar la reproducción
            
            # Obtener y mostrar el tiempo de reproducción en minutos
            tiempo_reproduccion = self.obtener_tiempo_reproduccion()
            if tiempo_reproduccion is not None:
                # Si el tiempo no ha cambiado, significa que la reproducción está detenida
                if tiempo_reproduccion_anterior is not None and tiempo_reproduccion == tiempo_reproduccion_anterior:
                    self.contador_bandera += 1
                    self.barra_aumento = False
                    print(f"Barra de {self.channelName} está detenida, intentando poner play")
                    print(f"Intento numero : {self.contador_bandera} de {self.channelName}")
                    # print("El tiempo de reproducción no ha cambiado. Deteniendo y reiniciando...")
                    if tiempo_reproduccion != "00:00" and self.contador_bandera >= 1:
                        self.enviar_comando("stop")  # Detener la reproducción
                        time.sleep(1.5)  # Esperar un momento antes de volver a reproducir
                        self.enviar_comando("play")  # Reanudar la reproducción
                        time.sleep(1)
                    # tiempo_reproduccion_anterior = "00:00"
                else:
                    self.barra_aumento = True
                    self.contador_bandera = 0
                    self.contador_reinicios = 0
                    tiempo_reproduccion_anterior = tiempo_reproduccion

                if self.contador_bandera > 3:
                    self.barra_aumento = False
                    self.contador_bandera = 0
                    #Este contador de reinicios solo se aumenta cuando son seguidos los reinicios, si se puede reproducir se reinicia el contador de reinicios jaja
                    self.contador_reinicios += 1
                    print(f"Maximo de intentos alcanzados reiniciando canal {self.channelName}")
                    self.reiniciar_canal()

                if self.contador_reinicios > 3:
                    "Correo se envía cuando se han hecho más de 3 reinicios sin exito de reproducir el contenido"
                    enviar_correo()
            
            time.sleep(5)  # Espera 5 segundos antes de volver a verificar
    
    def obtener_tiempo_reproduccion(self):
        """Obtiene el tiempo de reproducción actual de VLC en formato mm:ss."""
        try:
            tn = telnetlib.Telnet(self.HOST, self.vlc_telnet_port)
            tn.read_until(b"Password: ")
            tn.write(self.PASSWORD.encode("ascii") + b"\n")
            tn.write(b"get_time\n")  # Obtener el tiempo de reproducción
            salida = tn.read_until(b">").decode("ascii")
            tn.close()

            # Procesar la salida para obtener los segundos y convertirlos
            tiempo_str = salida.split("\n")[2].strip()  # El valor de tiempo está en la salida
            if tiempo_str == ">":
                return None  # Si no se obtiene un tiempo válido, retornar None
            
            self.on_message(f"Tiempo de reproducción : {tiempo_str} segundos")
            segundos = int(tiempo_str)  # Convertir la cadena a un entero
            self.current_time = segundos
            tiempo_formateado = convertir_a_minutos_segundos(segundos)
            return tiempo_formateado
        
        except Exception as e:
            return None

    def enviar_comando(self,comando):
        """Conecta a VLC vía Telnet y envía un comando."""
        try:
            tn = telnetlib.Telnet(self.HOST, self.vlc_telnet_port)
            tn.read_until(b"Password: ")
            tn.write(self.PASSWORD.encode("ascii") + b"\n")
            tn.write(comando.encode("ascii") + b"\n")
            tn.write(b"quit\n")  # Cierra la conexión después de enviar el comando
            print(f"Comando enviado: {comando}")
        except Exception as e:
            print("Error al conectar con VLC:", e)

    def on_message(self,message):

        message = str(message)
        if message.find("state playing"):
            message = message.replace("state playing",f"Estado Reproduciendo")
        if message.find("state paused"):
            message = message.replace("state paused","Estado Pausado")
        if message.find("state stopped"):
            message = message.replace("state stopped","Estado Detenido")
        message = message.replace(">","").replace("Welcome, Master","").rstrip().strip()
        if len(message) < 1:
            return
        ahora = datetime.now()
        with open(self.log_file, "a+", encoding="utf-8") as f:
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
    
    def reiniciar_canal(self):
        db =  dbase()
        channels = db.read("channel","*",{"port":self.port,"program":"VLC"})
        api_token = db.read("configuration", "*", {"name": "api_token"})[0]
                    
        if len(channels) < 1:
            print("canal no encontrado")
            return
        
        r = requests.post("http://127.0.0.1:5000/apagarCanal",data={"id":self.channel_id},headers={"Authorization":api_token["value"]})                
        print("El tiempo de reproducción no ha cambiado. Deteniendo y reiniciando...")
        db2 =  dbase()
        api_token2 = db2.read("configuration", "*", {"name": "api_token"})[0]
        r = requests.post("http://127.0.0.1:5000/encenderCanal",data={"id":self.channel_id},headers={"Authorization":api_token2["value"]})

