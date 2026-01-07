"""ESTE CONTROLLER INICIALIZA CONTROLADORES QUE REQUIERAN LOOPS INFINITOS EN SEGUNDO PLANO
EJ :
    BUCLE INFINITO DE MQTT
    BUCLE INFINITO DE CODIFICACION DE VIDEOS
    etc...

#NOTA : 
    Si no se requiere bucle infinito puedes ignorarlo ya que no se inicializara algun bucle pero si la instancia
# import Controllers.MqttController as MqttController
# import Controllers.PorteroController as PorteroController
# import Controllers.VideoController as VideoController

# mqtt = MqttController.Mqtt
# portero = PorteroController.portero
# video = VideoController.video

# mqttInstance = mqtt()
# porteroInstance = portero()
# videoInstance = video()

#Aqui van variables de instancias Ej:
# VideoController.mqtt = mqttInstance
"""

from pathlib import Path
ABSOLUTE_PATH =  str(Path(__file__).parent.parent)

if __name__ == "__main__":
    import sys
    sys.path.append(ABSOLUTE_PATH)  # Agregando el area de trabajo al path superior



#%IMPORT%

#%DECLARE%

#%INSTANCE%


class start():
    def __init__(self):
        print("INICIALIZANDO CONTROLADORES")
        self.classes = {}

        #Si alguna funcion de las clases tiene el decorador @loop se iniciara esa funcion con la instancia declarada
        #%DICT_CLASS%
        self.start_loops()
        

    def start_loops(self):
        #Creamos lista de metodos donde almacenaremos los metodos decorados con "loop"
        metodos = []
        #Iteramos cada clase del diccionario classes y guardamos en metodos
        for clase in self.classes:
            for nombre, metodo in clase.__dict__.items():
                if callable(metodo) and str(metodo).count("loop.<locals>")>0:
                   print(f"Iniciando metodo {nombre} del controller {clase.__name__}")
                   metodos.append((nombre, metodo,clase))

        #Iteramos los metodos que se van a ejecutar y con la clase guardada obtenemos la instancia del diccionario
        for nombre, metodo_decorado,clase in metodos:
            instancia = self.classes.get(clase)
            #Finalmente ejecutamos la funcion pasandole el parametro self osea la instancia de su clase
            metodo_decorado(instancia)
            
if __name__ == "__main__":
    start()



