from pathlib import Path
ABSOLUTE_PATH =  str(Path(__file__).parent.parent)

if __name__ == "__main__":
    import sys
    sys.path.append(ABSOLUTE_PATH)  # Agregando el area de trabajo al path 
    

import subprocess
import os,psutil,sys
from time import sleep
import zipfile
import shutil
import json
from obswebsocket import obsws, requests
import ffmpeg
from Controllers.audio_video import * 
import json
import os

def resolver_ruta(ruta_relativa):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, ruta_relativa)
    return os.path.join(os.path.abspath('.'), ruta_relativa)

RUTA_LOGOS = r"C:\xampp\htdocs\ip-tv-manager\public\storage\images"
RUTA_STREAMING = r"C:\xampp\htdocs\ip-tv-manager\public\streaming"
RUTA_CANALES = os.path.dirname(os.getcwd())+"\\OBS"

if not os.path.exists(RUTA_CANALES):
    os.mkdir(RUTA_CANALES)

def is_exe_running(exe_path):
    """
    Verifica si un archivo ejecutable específico está en ejecución.
    
    :param exe_path: Ruta completa del ejecutable (str).
    :return: True si el proceso está en ejecución, False en caso contrario.
    """
    exe_path = exe_path.lower()  # Normalizar ruta en minúsculas para evitar problemas de comparación
    for process in psutil.process_iter(['pid', 'exe']):  # Obtener PID y ruta de ejecución
        try:
            if process.info['exe'] and process.info['exe'].lower() == exe_path:
                return process.pid  # El proceso está en ejecución
        except (psutil.NoSuchProcess, psutil.AccessDenied, psutil.ZombieProcess):
            pass  # Ignorar procesos que ya no existen o que no se pueden acceder

    return False  # No se encontró el proceso en ejecución

def configurate_stream(ip="", port="", channel="", path_url="", logo="", stream_mode="RTP"):
    """
    Configura y genera el comando para iniciar una transmisión con VLC en modo RTP o HTTP.
    
    :param ip: Dirección IP de destino para RTP.
    :param port: Puerto de transmisión.
    :param channel: Nombre del canal.
    :param path_url: Ruta del archivo de entrada o URL del stream.
    :param logo: Nombre del archivo de logo (si aplica).
    :param stream_mode: Modo de transmisión ("RTP" o "HTTP").
    :return: Comando de VLC listo para ejecutarse.
    """

    # Configuración del comando según el modo de transmisión
    if stream_mode == "RTP":
        vlc_conf = f" :sout=#rtp{{dst={ip},port={port},mux=ts}} "
    elif stream_mode == "HTTP":
        vlc_conf = f" :sout=#http{{mux=ts,dst=:{port}/}} "
    else:
        raise ValueError("Modo de transmisión no válido. Usa 'RTP' o 'HTTP'.")

    # Ruta al ejecutable de VLC
    vlc_path = "vlc"
    telnet_port = int(port) - 1000

    # Comando final según el tipo de fuente
    if os.path.isdir(path_url) or os.path.isfile(path_url):
        return f'{vlc_path} "{path_url}" {vlc_conf} --volume=320 --sout-all --sout-keep --random --loop --network-caching=10000 --file-caching=6000 --extraintf telnet --telnet-password=alcafi-tv-2025 --telnet-port={telnet_port}'
    
    if path_url.startswith(("http://", "https://")):
        return f'{vlc_path} "{path_url}" {vlc_conf} --sout-all --sout-keep --loop --repeat --network-caching=10000 --file-caching=6000 --extraintf telnet --telnet-password=alcafi-tv-2025 --telnet-port={telnet_port}'

    return f'{vlc_path} dshow:// :dshow-vdev="{path_url}" {vlc_conf} :dshow-adev= :dshow-size=1920x1080 :dshow-aspect-ratio=16:9 :dshow-fps=30 :no-dshow-config :no-dshow-tuner :dshow-audio-channels=2 :dshow-audio-samplerate=44100 :dshow-audio-bitspersample=16 :live-caching=3000 :sout-keep --extraintf telnet --telnet-password=alcafi-tv-2025 --telnet-port={telnet_port}'

def detener_proceso_por_pid(pid):
    """
    Detiene un proceso por su PID en Windows o Linux/macOS.

    :param pid: Identificador del proceso (PID).
    :return: Mensaje indicando si se detuvo correctamente o si hubo un error.
    """
    if not isinstance(pid, int) or pid <= 0:
        return "Error: PID inválido."

    try:
        if sys.platform == "win32":
            # Windows: usar 'taskkill /PID PID /F'
            resultado = subprocess.run(["taskkill", "/PID", str(pid), "/F"], capture_output=True, text=True)
            if resultado.returncode == 0:
                return f"Proceso con PID {pid} detenido exitosamente."
            else:
                return f"Error al intentar detener el proceso con PID {pid}. {resultado.stderr}"
    except ProcessLookupError:
        return f"Error: No se encontró el proceso con PID {pid}."
    except PermissionError:
        return f"Error: No tienes permisos para detener el proceso con PID {pid}."
    except Exception as e:
        return f"Error inesperado: {str(e)}"

def lanzar_vlc(comando):
    """
    Lanza VLC en segundo plano y obtiene su PID exacto, incluso si hay múltiples instancias.

    :param comando: Comando de VLC como string.
    :return: PID real del proceso VLC recién iniciado.
    """
    try:
        # Obtener lista de PIDs de VLC antes de iniciar el nuevo proceso
        pids_antes = {proc.pid for proc in psutil.process_iter(attrs=['pid', 'name']) if "vlc" in proc.info['name'].lower()}

        # Iniciar VLC en segundo plano
        proceso = subprocess.Popen(comando, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        # Esperar un breve tiempo para que VLC inicie
        sleep(1.5)
        # Buscar el nuevo PID de VLC (el que no estaba antes)
        pid_vlc = None
        for proc in psutil.process_iter(attrs=['pid', 'name']):
            if "vlc" in proc.info['name'].lower() and proc.pid not in pids_antes:
                pid_vlc = proc.pid
                break  # Tomamos solo el PID recién iniciado

        if pid_vlc:
            print(f"VLC iniciado con éxito. PID real: {pid_vlc}")
            return pid_vlc
        else:
            print("Error: No se pudo encontrar el proceso VLC recién iniciado.")
            return None

    except FileNotFoundError:
        print("Error: VLC no está instalado o no se encuentra en el PATH.")
        return None
    except subprocess.SubprocessError as e:
        print(f"Error al ejecutar VLC: {e}")
        return None

def lanzar_obs(channel,logo,source,id):

    """
    Lanza OBS en segundo plano y obtiene su PID exacto, incluso si hay múltiples instancias.

    :param comando: Comando de OBS como string.
    :return: PID real del proceso OBS recién iniciado.
    """
    
    obs_exe_path = RUTA_CANALES + f"\\{channel}\\bin\\64bit\\obs64.exe"
    if not os.path.exists(obs_exe_path):
        agregar_canal_con_obs(channel,logo,source,id)

    working_directory = f"{RUTA_CANALES}\\{channel}\\bin\\64bit\\"
    SAFE_MODE_PATH = f"{RUTA_CANALES}\\{channel}\\config\\obs-studio\\safe_mode"

    if (is_exe_running(obs_exe_path)):
        print("OBS IS CURRENTY RUNNING!")
        return
    try:    
        comando = f'start "" "{obs_exe_path}" --startrecording'
        # os.startfile(obs_exe_path)
        # proceso = subprocess.Popen(comando, shell=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        # print(comando,proceso)
        if os.path.exists(SAFE_MODE_PATH):
            os.remove(SAFE_MODE_PATH)
        subprocess.Popen([obs_exe_path, "--startrecording"], cwd=working_directory)
        if os.path.exists(SAFE_MODE_PATH):
            os.remove(SAFE_MODE_PATH)

        pid = is_exe_running(obs_exe_path)
        return pid
    
    except Exception as e:
        print("OBS EXCEPTION! ",e)
        return False

def agregar_canal_con_obs(channel,logo,source,id):
    """Agrega carpeta nueva de obs en ruta OBS, para manejor de streaming con OBS"""
    ruta_nuevo_canal = RUTA_CANALES+f"\\{channel}"
    obs_exe_path = RUTA_CANALES + f"\\{channel}\\bin\\64bit\\obs64.exe"
    
    if not os.path.exists(ruta_nuevo_canal):
        os.mkdir(ruta_nuevo_canal)
    
    zip_origen = resolver_ruta("dependencias/obs.zip")  # Cambia esta ruta a donde tengas xampp.zip

    destino = ruta_nuevo_canal

    # Copia y descomprime
    shutil.copy(zip_origen, destino)
    with zipfile.ZipFile(destino+"/obs.zip", "r") as zip_ref:
        zip_ref.extractall(destino)
    
    modificar_puerto_ws(channel,id)# Modifica el puerto de acceso al obs cuando está prendido
    modificar_logo(channel,logo) # Modifica logo directamente en los archivos (funciona solo cuando esta cerrado OBS)
    configurar_path(channel) # Creamos la carpeta de streaming para aplicar la configuracion en obs
    cambiar_fuente_de_video_sin_ws(channel,source)
    configurar_tuna_path(channel)
    now_playing_source(channel)
    

    os.remove(destino+"/obs.zip") # Removemos el .zip de la carpeta para evitar basura

def configurar_path(channel):
    basic_ini = RUTA_CANALES+f"\\{channel}\\config\\obs-studio\\basic\\profiles\\Sin_Título\\basic.ini"
    new_path = RUTA_STREAMING + f"\\{channel}"

    #Creamos la carpeta
    if not os.path.exists(new_path):
        os.mkdir(new_path)
        
    with open(basic_ini,"a+",encoding="utf-8") as file:
        file.seek(0)
        json_ = file.read()

        inicio_linea = json_.find("FFFilePath")
        fin = inicio_linea+len(json_[json_.find("FFFilePath"):].splitlines()[0])
        new_file = json_.replace(json_[inicio_linea:fin],f"FFFilePath={new_path}")
            
        inicio_linea = new_file.find("FFFormat")
        fin = inicio_linea+len(new_file[new_file.find("FFFormat"):].splitlines()[0])
        new_file = new_file.replace(new_file[inicio_linea:fin],f"FFFormat=hls")

        file.seek(0)
        file.truncate(0)

        file.write(new_file)

def configurar_tuna_path(channel):
    """"""
    tuna_config = RUTA_CANALES+f"\\{channel}\\config\\obs-studio\\plugin_config\\tuna\\outputs.json"
    new_path = RUTA_CANALES + f"\\{channel}\\now-playing\\Track.txt"

    #Creamos la carpeta
    if not os.path.exists(new_path):
        os.mkdir(new_path)
        
    with open(tuna_config,"a+",encoding="utf-8") as file:
        file.seek(0)
        json_ = file.read()

        jsonObject = json.loads(json_)[0]  
        jsonObject["output"] = new_path

        file.seek(0)
        file.truncate(0)

        new_content = json.dumps(jsonObject,indent=4)

        file.write(f"[{new_content}]")

def now_playing_source(canal):
    """Modifica logo de obs en base a el canal"""
    ruta_a_canal = RUTA_CANALES + f"\\{canal}"
    obs_exe_path = RUTA_CANALES + f"\\{canal}\\bin\\64bit\\obs64.exe"
    now_playing_file =  RUTA_CANALES + f"\\{canal}\\now-playing\\Movie.html"

    if (is_exe_running(obs_exe_path)):
        print("OBS esta siendo ejecutado en este momento y no puede modificar sus configuraciones")
        return
    
    if not os.path.exists(ruta_a_canal):
        print("El canal solicitado no existe")
        return
    
    if not os.path.exists(now_playing_file):
        print("Verifica que la ruta del logo sea correcta")
        return
    
    config_file = RUTA_CANALES + f"\\{canal}\\config\\obs-studio\\basic\\scenes\\Sin_Título.json"
    config_bak = RUTA_CANALES + f"\\{canal}\\config\\obs-studio\\basic\\scenes\\Sin_Título.json.bak"
    new_content = ""
    with open(config_file,"a+",encoding="utf-8") as file:
        file.seek(0)
        json_ = file.read()
        configObject = json.loads(json_)

        # iteramos el json para encontrar la configuración y cambiarla
        for key in configObject.get("sources"):
            for key2 in key:
                if key2 == "name" and key.get("name") == "now":
                    key["settings"]["local_file"] = now_playing_file
        
        file.seek(0)
        file.truncate(0)
        
        new_content = json.dumps(configObject,indent=4)

        file.write(new_content)
        with open(config_bak,"a+",encoding="utf-8") as bak:
            bak.seek(0)
            bak.truncate(0)
            bak.write(json.dumps(new_content))

def modificar_puerto_ws(canal,id):
    """Toma el id del canal y ese será el ultimo numero del puerto en los ws"""
    
    config_file = RUTA_CANALES + f"\\{canal}\\config\\obs-studio\\plugin_config\\obs-websocket\\config.json"
    with open(config_file,"a+",encoding="utf-8") as file:
        file.seek(0)
        json_ = file.read()
        configObject = json.loads(json_)

        # iteramos el json para encontrar la configuración y cambiarla
        configObject["auth_required"] = True
        configObject["server_enabled"] = True
        configObject["server_port"] = f"{445}{id}"

        file.seek(0)
        file.truncate(0)

        new_content = json.dumps(configObject,indent=4)
        file.write(new_content)

def modificar_logo(canal,logo):
    """Modifica logo de obs en base a el canal"""
    ruta_a_canal = RUTA_CANALES + f"\\{canal}"
    obs_exe_path = RUTA_CANALES + f"\\{canal}\\bin\\64bit\\obs64.exe"
    if (is_exe_running(obs_exe_path)):
        print("OBS esta siendo ejecutado en este momento y no puede modificar sus configuraciones")
        return
    if not os.path.exists(ruta_a_canal):
        print("El canal solicitado no existe")
        return
    if not os.path.exists(logo):
        print("Verifica que la ruta del logo sea correcta")
        return
    config_file = RUTA_CANALES + f"\\{canal}\\config\\obs-studio\\basic\\scenes\\Sin_Título.json"
    config_bak = RUTA_CANALES + f"\\{canal}\\config\\obs-studio\\basic\\scenes\\Sin_Título.json.bak"
    new_content = ""
    with open(config_file,"a+",encoding="utf-8") as file:
        file.seek(0)
        json_ = file.read()
        configObject = json.loads(json_)

        # iteramos el json para encontrar la configuración y cambiarla
        for key in configObject.get("sources"):
            for key2 in key:
                if key2 == "name" and key.get("name") == "Imagen":
                    key["settings"]["file"] = logo
        
        file.seek(0)
        file.truncate(0)
        
        new_content = json.dumps(configObject,indent=4)

        file.write(new_content)
        with open(config_bak,"a+",encoding="utf-8") as bak:
            bak.seek(0)
            bak.truncate(0)
            bak.write(json.dumps(new_content))

def obtener_pass_ws(canal):
    """Obtiene contraseña de authenticación para servidor de ws"""
    config_file = RUTA_CANALES + f"\\{canal}\\config\\obs-studio\\plugin_config\\obs-websocket\\config.json"
    with open(config_file,"a+",encoding="utf-8") as file:
        file.seek(0)
        json_ = file.read()
        configObject = json.loads(json_)

        return configObject.get("server_password")

def modificar_logo_ws(canal,logo,id):
    obs_exe_path = RUTA_CANALES + f"\\{canal}\\bin\\64bit\\obs64.exe"
    ruta_a_canal = RUTA_CANALES + f"\\{canal}"

    if (not is_exe_running(obs_exe_path)):
        print("OBS no esta siendo ejecutado en este momento, no puede modificar sus configuraciones con ws")
        return
    
    if not os.path.exists(ruta_a_canal):
        print("El canal solicitado no existe")
        return
    if not os.path.exists(logo):
        print("Verifica que la ruta del logo sea correcta")
        return
    
    nueva_ruta = logo
    HOST = "localhost"
    PORT = f"{445}{id}"  # Cambia si tienes otro puerto en OBS
    PASSWORD = obtener_pass_ws(canal) # Si OBS tiene contraseña, ponla aquí
    fuente_obs = "Imagen"
    ws = obsws(HOST, PORT, PASSWORD)
    ws.connect()
    respuesta = ws.call(requests.GetInputSettings(inputName=fuente_obs))
    tipo_fuente = respuesta.datain.get("inputKind", "")
    print(f"🔍 La fuente '{fuente_obs}' es de tipo: {tipo_fuente}")
    if tipo_fuente == "image_source":
        # Cambiar la imagen de la fuente en OBS
        ws.call(requests.SetInputSettings(
            inputName=fuente_obs,
            inputSettings={"file": nueva_ruta},
            overlay=False
        ))
        print(f"✅ Imagen cambiada a: {nueva_ruta}")
    else:
        print(f"❌ ERROR: La fuente '{fuente_obs}' no es una 'Fuente de imagen' (image_source).")
    # Desconectar de OBS
    ws.disconnect()

def get_device_id(video_device_name):
    """Obtiene el ID global de un dispositivo de captura de video basado en su nombre."""
    devices = get_video_input_devices()
    for device in devices:
        if video_device_name in device["name"]:
            print(f"🔍 Dispositivo encontrado: {device['name']} | ID: {device['id']}")
            return device["id"]
    
    print("❌ No se encontró el dispositivo en la lista.")
    return None

def set_source_visible(ws:obsws,source,visibility):
            # Obtener el ID del ítem en la escena
        response_scene = ws.call(requests.GetCurrentProgramScene())
        scene_name = response_scene.datain["currentProgramSceneName"]  # Nombre de la escena actual

        # Obtener el ID del ítem en la escena actual
        response_item = ws.call(requests.GetSceneItemId(sceneName=scene_name, sourceName=source))
        scene_item_id = response_item.datain["sceneItemId"]

        # Gestionar visibilidad sin necesidad de especificar la escena manualmente
        ws.call(requests.SetSceneItemEnabled(sceneName=scene_name, sceneItemId=scene_item_id, sceneItemEnabled=visibility))

def cambiar_fuente_de_video_ws(canal, fuente, id):
    """Cambia la fuente de video del canal de OBS con WebSocket y gestiona la visibilidad."""

    obs_exe_path = RUTA_CANALES + f"\\{canal}\\bin\\64bit\\obs64.exe"
    ruta_a_canal = RUTA_CANALES + f"\\{canal}"

    if not is_exe_running(obs_exe_path):
        print("OBS no está siendo ejecutado en este momento, no puede modificar sus configuraciones con WS")
        return

    if not os.path.exists(ruta_a_canal):
        print("El canal solicitado no existe")
        return

    HOST = "localhost"
    PORT = f"445{id}"  # Cambia si tienes otro puerto en OBS
    PASSWORD = obtener_pass_ws(canal)  # Si OBS tiene contraseña, ponla aquí
   
    ws = obsws(HOST, PORT, PASSWORD)
    ws.connect()

    if not os.path.exists(fuente):
        print(f"⚠️ La fuente '{fuente}' no existe. Se usará la capturadora de video.")
        nueva_ruta = "USB2 Video"  # Asignar la fuente de captura de video por defecto
        video_device_id = get_device_id(nueva_ruta)
        if not video_device_id:
            print("❌ No se pudo obtener el ID del dispositivo de captura de video.")
            return
        nueva_ruta = video_device_id
        audio_source = obtener_device_id_por_nombre(get_audio_source(fuente)) # Asignar la fuente de captura de audio
        fuente_obs = "Capturadora"
    else:
        nueva_ruta = fuente  # Se mantiene la ruta del archivo de video
        fuente_obs = "Video"

    respuesta = ws.call(requests.GetInputSettings(inputName=fuente_obs))
    tipo_fuente = respuesta.datain.get("inputKind", "")
    print(f"🔍 La fuente '{fuente_obs}' es de tipo: {tipo_fuente}")
    
    if tipo_fuente in ["image_source", "ffmpeg_source", "vlc_source", "dshow_input"]:
        settings = {"file": nueva_ruta} if tipo_fuente != "vlc_source" else {
            "playlist": [{"value": nueva_ruta}],
            "shuffle": True,  # Activar mezcla de lista de reproducción
            "playback_behavior": "pause_unseen_resume_seen"  # Configuración para pausar cuando no sea visible
        }
        print(tipo_fuente)
        if tipo_fuente == "dshow_input":
            nueva_ruta = str(nueva_ruta).replace("#","#22").replace(r"\usb","\\usb").replace(r"\global","\\global").replace("\"","")
            nueva_ruta = f"{fuente}:{nueva_ruta}"
            settings = {"video_device_id": nueva_ruta, "last_video_device_id": nueva_ruta}  # Asignar dispositivo de captura de video con ID
        
        ws.call(requests.SetInputSettings(
            inputName=fuente_obs,
            inputSettings=settings,
            overlay=False
        ))
        print(f"✅ Fuente de video cambiada a: {nueva_ruta}")
        
        if not os.path.exists(fuente):
            ws.call(requests.SetInputSettings(
                inputName="Capturadora_audio",
                inputSettings={"device": 0},
                overlay=False
            ))
            print(f"✅ Fuente de audio cambiada a: {audio_source}")
    
        (set_source_visible(ws,"Capturadora",True),set_source_visible(ws,"Video",False)) if fuente_obs == "Capturadora" else (set_source_visible(ws,"Capturadora",False),set_source_visible(ws,"Video",True))

        print(f"👀 Visibilidad actualizada: Capturadora {'Visible' if fuente_obs == 'Capturadora' else 'Oculta'}, Video {'Visible' if fuente_obs == 'Video' else 'Oculto'}")
    else:
        print(f"❌ ERROR: La fuente '{fuente_obs}' no es compatible para cambio de video.")
    
    ws.disconnect()

def cambiar_fuente_de_video_sin_ws(canal, fuente):
    """Cambia la fuente de video del canal de OBS modificando directamente el archivo de configuración."""

    ruta_config = RUTA_CANALES + f"\\{canal}\\config\\obs-studio\\basic\\scenes\\Sin_Título.json"
    ruta_a_canal = RUTA_CANALES + f"\\{canal}"

    if not os.path.exists(ruta_a_canal):
        print("El canal solicitado no existe")
        return

    if not os.path.exists(ruta_config):
        print("No se encontró el archivo de configuración de OBS.")
        return

    with open(ruta_config, "r", encoding="utf-8") as file:
        config_data = json.load(file)

    fuente_obs = "Video"
    nueva_ruta = fuente

    if not os.path.exists(fuente):
        print(f"⚠️ La fuente '{fuente}' no existe. Se usará la capturadora de video.")
        nueva_ruta = "USB2 Video"  # Asignar la fuente de captura de video por defecto
        video_device_id = get_device_id(nueva_ruta)
        if not video_device_id:
            print("❌ No se pudo obtener el ID del dispositivo de captura de video.")
            return
        nueva_ruta = str(video_device_id).replace("#","#22").replace(r"\usb","\\usb").replace(r"\global","\\global").replace("\"","")
        nueva_ruta = f"{fuente}:{nueva_ruta}"
        audio_source = get_audio_source(fuente) # Asignar la fuente de captura de audio
        fuente_obs = "Capturadora"

    # Buscar la fuente dentro del archivo JSON y actualizar según su tipo
    for scene in config_data.get("sources", []):
        if scene.get("name") == fuente_obs:
            if scene.get("settings") is not None:
                if fuente_obs == "Capturadora":
                    # Para capturadora de video se usa `video_device_id` y `last_video_device_id`
                    scene["settings"]["video_device_id"] = nueva_ruta
                    scene["settings"]["last_video_device_id"] = nueva_ruta
                else:
                    # Para fuentes de video locales se usa `local_file`
                    scene["settings"]["local_file"] = nueva_ruta
                break

    # Ajustar la visibilidad de las fuentes
    for scene in config_data.get("sources", []):
        if scene.get("id") == "scene" and "settings" in scene and "items" in scene["settings"]:
            for item in scene["settings"]["items"]:
                if item.get("name") == "Capturadora":
                    item["visible"] = (fuente_obs == "Capturadora")  # Mostrar Capturadora si se usa
                elif item.get("name") == "Video":
                    item["visible"] = (fuente_obs == "Video")  # Mostrar Video si se usa

    # Guardar cambios en el archivo JSON de configuración
    with open(ruta_config, "w", encoding="utf-8") as file:
        json.dump(config_data, file, indent=4)

    print(f"✅ Fuente de video cambiada a: {nueva_ruta} en el archivo de configuración.")
    print(f"👀 Visibilidad actualizada: Capturadora {'Visible' if fuente_obs == 'Capturadora' else 'Oculta'}, Video {'Visible' if fuente_obs == 'Video' else 'Oculto'}")

    # Si se está usando la capturadora, cambiar también la fuente de audio
    if fuente_obs == "Capturadora":
        for scene in config_data.get("sources", []):
            if scene.get("name") == "Capturadora_audio":
                if scene.get("settings") is not None:
                    scene["settings"]["device_id"] = obtener_device_id_por_nombre(audio_source)  # Cambiar el dispositivo de audio
                    break

        with open(ruta_config, "w", encoding="utf-8") as file:
            json.dump(config_data, file, indent=4)

        print(f"✅ Fuente de audio cambiada a: {audio_source}")


if __name__ == "__main__":
    "Pruebas unitarias"
    # lanzar_obs("asd")
    configurar_tuna_path("asd")
    # configurar_path("asd")
    # cambiar_fuente_de_video_ws("asd","USB2 Video","5")
    # cambiar_fuente_de_video_sin_ws("asd",r"C:\Users\Leo Del Toro\Downloads\pelis")
    # modificar_logo("asd",r"C:\Users\Leo Del Toro\Downloads\HBO_logo.png")