from pathlib import Path
ABSOLUTE_PATH =  str(Path(__file__).parent.parent)

if __name__ == "__main__":
    import sys
    sys.path.append(ABSOLUTE_PATH)  # Agregando el area de trabajo al path 
    

try:
    import Public.Variables.public as public
    from Librarys.Librarys import subprocess, datetime,ONVIFCamera
except:
    import subprocess
    from datetime import datetime
    from onvif import ONVIFCamera

class ConexionCamara():
    def __init__(self,ip,user,password,port=80):
          self.ip = ip
          self.user = user
          self.password = password
          self.port = port

    def comprobar_conexion(self):
        """True : conection success
        False : conection Failed :("""
        #Comprobamos con el metodo ping la primer etapa:
        isPing = self.ping()
        print("#-------------#")
        if not isPing:
            print("❌ ping failed")
            return False

        print("✅ ping success")

        #Comprobamos con la libreria Onvif para conectarse a la camara y obtener sus datos
        isOnvif = self.comprobarOnvif()

        if not isOnvif:
            print("❌ onvif failed")
            return False

        print("✅ onvif success")

        #Si no hubo errores la camara si esta conectada!
        return True

    def ping(self):
        command = ['ping',"-n", '1', self.ip]
        response = subprocess.run(command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True, creationflags=subprocess.CREATE_NO_WINDOW)
        output = response.stdout


        if "bytes=" in output:
            return True
        else:
            return False

    def comprobarOnvif(self):
        error = False
        if __file__.find("pyd") == -1:
            now = datetime.now()

        try:
            ONVIFCamera(self.ip,self.port,self.user,self.password)
        except:
            error = True


        if __file__.find("pyd") == -1:
            diferencia = datetime.now()
            print("Tiempo de ejecucion : ",diferencia-now)

        if error:
             return False

        return True





if __name__ == "__main__":
    print(ConexionCamara("192.168.16.39","sa","sw").comprobar_conexion())