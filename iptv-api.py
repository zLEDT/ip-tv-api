import subprocess
import pymysql.cursors
from mysql import *
import os,psutil,sys
from flask import Flask, request, jsonify
from flask_cors import CORS
from Database.database import *
from Librarys.utility import *
from Controllers.execute import * 
import subprocess
import os,psutil,sys
from Controllers.loop import loop
from time import sleep
import zipfile
import shutil
import json
from obswebsocket import obsws, requests
import ffmpeg
from Controllers.audio_video import * 
import json
import os
from Controllers.middleware import *
from Controllers.VLCController import *
app = Flask(__name__)
CORS(app, origins=[
    "http://localhost:8000"
    
    ])

@app.route("/encenderCanal", methods=["POST"])
@tokenAuth
def encender_canal():
    canal_id = request.form.get("id")
    if canal_id is None:
        return jsonify({"error": "Se requiere un ID"}), 400
    db = dbase()
    channels = db.read("channel","*",{"id":canal_id})
    if len(channels) < 1:
        return "canal no encontrado"
    channel = channels[0]
    name = channel["name"]
    port = channel["port"]
    ip = channel["ip"]
    url = channel["url"]
    id = channel["id"]
    pid = channel["pid"]
    program :str = channel["program"]
    logo = channel["logo"]
    if pid == 0 :
        status = False
    status = check_status(pid,program.lower())

    if(status and pid != 0):
        print(f"Canal {name} ya esta en uso y no puede ser ejecutado")
        return f"Canal {name} ya esta en uso y no puede ser ejecutado"

    if(program == "OBS"):
        logo = channel["logo"]
        logo = f"{RUTA_LOGOS}\\{logo}"
        pid_nuevo = lanzar_obs(name,logo,url,id)
    else:
        comando = configurate_stream(ip,port,name,url,logo,db.stream_mode)
        pid_nuevo = lanzar_vlc(comando)

    pid_ya_existe = db.read("channel","count(pid) as count",{"pid":pid_nuevo})[0]
    if not pid_ya_existe.get("count") and not status:
        db.update("channel",{"pid":pid_nuevo},{"id":id})
    else:
        return jsonify({"message":f"Canal {name} no se pudo iniciar, verifica la url manualmente y revisa la salida"}) 
        
    return jsonify({"message": f"Canal {canal_id} encendido"})

@app.route("/apagarCanal", methods=["POST"])
@tokenAuth
def apagar_canal():
    canal_id = request.form.get("id")
    if canal_id is None:
        return jsonify({"error": "Se requiere un ID"}), 400
    db = dbase()
    channels = db.read("channel","*",{"id":canal_id})
    if len(channels) < 1:
        return "canal no encontrado"
    
    channel = channels[0]
    name = channel["name"]
    port = channel["port"]
    ip = channel["ip"]
    url = channel["url"]
    id = channel["id"]
    pid = channel["pid"]
    logo = channel["logo"]
    program = channel["program"]
    if pid == 0 :
        status = False
    status = check_status(pid,program.lower())

    if(not status and pid != 0):
        print(f"Canal {name} ya está apagado")
        return f"Canal {name} ya está apagado"
    
    process_message = detener_proceso_por_pid(pid)        
    return f"Canal {name}  detenido con exito {process_message}"

@app.route("/encenderTodos", methods=["POST"])
@tokenAuth
def encender_todos():
    encender_segundo_plano()
    return jsonify({"message": "Todos los canales han sido encendidos"})

@loop
def encender_segundo_plano():
    db = dbase()
    channels = db.read("channel")
    for channel in channels:
        name = channel["name"]
        port = channel["port"]
        ip = channel["ip"]
        url = channel["url"]
        id = channel["id"]
        pid = channel["pid"]
        logo = channel["logo"]
        program = channel["program"]
        
        if pid == 0 :
            status = False
        status = check_status(pid,program.lower())

        if(status and pid != 0):
            print(f"Canal {name} ya esta en uso y no puede ser ejecutado")
            continue

        if(program == "OBS"):
            logo = channel["logo"]
            logo = f"{RUTA_LOGOS}\\{logo}"
            pid_nuevo = lanzar_obs(name,logo,url,id)
        else:
            comando = configurate_stream(ip,port,name,url,logo,db.stream_mode)
            pid_nuevo = lanzar_vlc(comando)

        pid_ya_existe = db.read("channel","count(pid) as count",{"pid":pid_nuevo})[0]
       
       
        if not pid_ya_existe.get("count") and not status:
            db.update("channel",{"pid":pid_nuevo},{"id":id})
        else:
            print({"message":f"Canal {name} no se pudo iniciar, verifica la url manualmente y revisa la salida"})
        
@app.route("/apagarTodos", methods=["POST"])
@tokenAuth
def apagar_todos():
    response = {}
    db = dbase()
    channels = db.read("channel")
    for channel in channels:
        name = channel["name"]
        port = channel["port"]
        ip = channel["ip"]
        url = channel["url"]
        id = channel["id"]
        pid = channel["pid"]
        logo = channel["logo"]
        program :str = channel["program"]
        if pid == 0 :
            status = False
        status = check_status(pid,program.lower())

        if(not status and pid != 0):
            response[name] = f"Canal {name} ya está apagado"
            continue

        process_message = detener_proceso_por_pid(pid)        
        response[name] = f"Canal {name} detenido con exito {process_message}"
        
    return jsonify({"message": "Todos los canales han sido apagados","channels":response})


def get_channels():
    db_instance = dbase()
    channels = db_instance.read("channel", ["id", "name", "pid"])
    return [{'id': channel['id'], 'name': channel['name'], 'pid': channel['pid']} for channel in channels]

def get_process_list(process_name):
    try:
        result = subprocess.run(
            ['powershell', '-Command', f"Get-Process {process_name} | Sort-Object StartTime -Descending | Select-Object Id"],
            capture_output=True, text=True
        )
        pids = re.findall(r'\b\d+\b', result.stdout)
        return [int(pid) for pid in pids]
    except Exception:
        return []

@app.route('/status', methods=['GET'])
@tokenAuth
def status():
    channels = get_channels()
    pids_vlc = get_process_list('vlc')
    pids_obs = get_process_list('obs64')
    active_pids = set(pids_vlc + pids_obs)
    result = []
    for channel in channels:
        is_active = 1 if channel['pid'] in active_pids and channel['pid'] != 0 else 0

        if consoles_dict.get(channel['id']) is not None:
            stability = consoles_dict.get(channel['id']).getStability()
        else:
            stability = "unknown"

        result.append({
            'id': channel['id'],
            'name': channel['name'],
            'status': is_active ,
            "stability" : stability
        })
    return jsonify(result)


@app.route("/log/<int:canal_id>", methods=["GET"])
@tokenAuth
def obtener_log_canal(canal_id):
    db = dbase()
    channels = db.read("channel", ["name"], {"id": canal_id})
    if not channels:
        return jsonify({"error": "Canal no encontrado"}), 404
    channel_name = channels[0]["name"]
    log_path = os.path.join("logs", f"{channel_name}.log")
    if not os.path.exists(log_path):
        return jsonify({"error": "Log no encontrado"}), 404
    with open(log_path, "r", encoding="utf-8") as f:
        lines = f.readlines()
        # reversed_content = ''.join(lines[::-1])
        reversed_content = ''.join(lines)
    return jsonify({"id": canal_id, "name": channel_name, "log": reversed_content})


@app.route("/mostrar",methods=["POST"])
@tokenAuth
def traer_al_frente():
    canal_id = request.form.get("id")

    if canal_id is None:
        return jsonify({"error": "Se requiere un ID"}), 400
    
    db = dbase()
    channels = db.read("channel","*",{"id":canal_id})
    if len(channels) < 1:
        return "canal no encontrado"

    pid = channels[0]["pid"]
    name = channels[0]["name"]
    id = channels[0]["id"]
    if consoles_dict.get(id) is None:
        return jsonify({"error": "Consola no encontrada"}), 404
    
    if consoles_dict.get(id).status == "offline":
        return jsonify({"error": "El canal no está encendido"}), 400


    bring_window_to_front(pid)
    return jsonify({"success":"true","data": f"Canal {name} traído al frente"})



consoles_dict = {}

def iniciar_consolas_vlc():
    db = dbase()
    channels = db.read("channel","*",{"program":"VLC"})
    for channel in channels:
        port = channel["port"]
        id = channel["id"]

        channel = console_vlc(port=port)
        channel.iniciar_monitoreo()
        consoles_dict.update({id:channel})
@loop
def task_schedule():
    iniciar_consolas_vlc()


class flask_obs:
    def __init__(self):
        pass
    
    @app.route("/cambiarLogo",methods=["POST"])
    @tokenAuth
    def cambiar_logo():
        id = request.form.get("id")

        db = dbase()

        if len(channels) < 1:
            return "canal no encontrado"
        
        channels = db.read("channel","*",{"id":id})
        channel = channels[0]
        id = channel["id"]
        logo = channel["logo"]
        logo = f"{RUTA_LOGOS}\\{logo}"
            
        obs_exe_path = RUTA_CANALES + f"\\{channel}\\bin\\64bit\\obs64.exe"
        if(is_exe_running(obs_exe_path)):
            modificar_logo_ws(channel,logo,id)
        else:
            modificar_logo(channel,logo)

        return jsonify({"message": "Logo actualizado en obs"})

    @app.route("/crearCanal",methods=["POST"])
    @tokenAuth
    def crear_canal():
        id = request.form.get("id")
        if id is None:
            print("id is none")
            return jsonify({"error": "Se requiere un ID"}), 400
        
        db = dbase()
        channels = db.read("channel","*",{"id":id})
        print(channels)
        if len(channels) < 1:
            print("channels len is less than 1")
            return "canal no encontrado"
        
        channel = channels[0]
        name = channel["name"]
        logo = channel["logo"]
        logo = f"{RUTA_LOGOS}\\{logo}"

        source = channel["url"]

        agregar_canal_con_obs(name,logo,source,id)
        



if __name__ == "__main__":
    todays_token()
    task_schedule()
    app.run()