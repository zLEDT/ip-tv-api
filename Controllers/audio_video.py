import subprocess
import re
import json

def list_video_devices():
    try:
        result = subprocess.run(['ffmpeg', '-list_devices', 'true', '-f', 'dshow', '-i', 'dummy'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        devices = result.stderr.split('\n')
        video_devices = [line for line in devices if 'video' in line.lower()]
        audio_devices = [line for line in devices if 'audio' in line.lower()]
        
        return video_devices,audio_devices
    except Exception as e:
        print(f"Error al listar dispositivos: {e}")
        return [], []

def get_audio_source(video_device_name):
    try:
        _,audio_devices = list_video_devices()
        
        for audio_device in audio_devices:
            video_device_names = video_device_name.split(" ")
            for video_device_name in video_device_names:
                if video_device_name in audio_device:
                    audio_name = audio_device.split('"')[1]
                    # print(f"Fuente de audio detectada: {audio_name}")
                    return audio_name
        
        print("No se encontró una fuente de audio asociada.")
        return None
    except Exception as e:
        print(f"Error al detectar la fuente de audio: {e}")
        return None

def get_video_input_devices():
    """Obtiene la lista de dispositivos de entrada de video y sus IDs globales en Windows usando ffmpeg."""
    try:
        result = subprocess.run(
            ["ffmpeg", "-list_devices", "true", "-f", "dshow", "-i", "dummy"],
            stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        devices = result.stderr.split("\n")
        video_devices = []
        current_device = None

        for line in devices:
            match_device = re.search(r'"([^"]+)"\s+\(video\)', line)  # Detectar nombres de dispositivos de video
            match_id = re.search(r'\\\\\?\\usb#.*', line)  # Detectar el ID global del dispositivo
            print(line)
            if match_device:
                current_device = match_device.group(1)
            
            if match_id and current_device:
                video_devices.append({"name": current_device, "id": match_id.group(0)})
                current_device = None  # Reset para el próximo dispositivo

        return video_devices
    except Exception as e:
        print(f"❌ Error al obtener dispositivos de entrada de video: {e}")
        return []

def obtener_device_id_por_nombre(nombre_dispositivo):
    """Obtiene el device_id (InstanceId) en formato limpio de un dispositivo de entrada de audio en Windows."""

    comando = 'powershell "Get-PnpDevice -Class AudioEndpoint | Select-Object FriendlyName, InstanceId | ConvertTo-Json"'
    
    try:
        resultado = subprocess.run(comando, shell=True, capture_output=True, text=True)
        dispositivos = json.loads(resultado.stdout)

        if isinstance(dispositivos, dict):  # Si solo hay un dispositivo, lo convierte en lista
            dispositivos = [dispositivos]

        for dispositivo in dispositivos:
            if nombre_dispositivo.lower() in dispositivo["FriendlyName"].lower():
                instance_id = dispositivo["InstanceId"]

                # Usar regex para extraer solo el identificador en formato correcto
                match = re.search(r'\{0\.0\.1\.\d+\}\.\{[0-9A-Fa-f\-]+\}', instance_id)
                if match:
                    return match.group(0).lower()

        print(f"❌ No se encontró un dispositivo con el nombre '{nombre_dispositivo}'.")
        return None

    except Exception as e:
        print(f"⚠️ Error al obtener la lista de dispositivos: {e}")
        return None
