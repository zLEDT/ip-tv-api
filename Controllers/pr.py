from obswebsocket import obsws, requests

# Configuración de la conexión a OBS
host = "localhost"
port = 4455
password = "tu_contraseña"  # Reemplaza con tu contraseña si la tienes

try:
    ws = obsws(host, port, password)
    ws.connect()
    print("Conexión a OBS establecida.")

    # Obtener la configuración actual de la escena
    escena_actual = ws.call(requests.GetScene("Escena"))

    # Buscar la fuente "Video" en la escena
    for item in escena_actual.getScene().getSourceItems():
        if item['name'] == "Video":
            # Modificar la visibilidad de la fuente
            item['visible'] = False
            break

    # Actualizar la escena con la nueva configuración
    ws.call(requests.SetScene("Escena", escena_actual.getScene()))

    print("Fuente 'Video' oculta en la escena 'Escena'.")

    # Cerrar la conexión a OBS
    ws.disconnect()
    print("Conexión a OBS cerrada.")

except Exception as e:
    print(f"Error: {e}")