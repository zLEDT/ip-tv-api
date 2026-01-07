from pathlib import Path
ABSOLUTE_PATH =  str(Path(__file__).parent.parent)

if __name__ == "__main__":
    import sys
    sys.path.append(ABSOLUTE_PATH)  # Agregando el area de trabajo al path 

import bcrypt
from Database.database import dbase
from flask import *
from datetime import datetime
import random
from functools import wraps
def todays_token():
    db = dbase()
    apiToken = db.read("configuration", "*", {"name": "api_token"})    
    
    salt = bcrypt.gensalt()
    
    first_param = datetime.now()
    second_param = salt 
    third_param = random.randbytes(5)

    pwd = (f"{first_param}{second_param}{third_param}").encode()
    
    new_token = bcrypt.hashpw(pwd,salt)
    if len(apiToken) == 0:
        db.create("configuration",{"name":"api_token","value":new_token})

    
    db.update("configuration",{"value":new_token},{"name":"api_token"})



def tokenAuth(funcion_original):
    @wraps(funcion_original)
    def funcion_en_segundo_plano(*args, **kwargs):
        if not 'Authorization' in request.headers:
            print("no se pudo acceder1")
            return error("invalid auth")
        
        token = request.headers['Authorization']
        db = dbase()
        api_token = db.read("configuration", "*", {"name": "api_token"})[0]
        print(api_token["value"])
        if api_token["value"] != token:

            print("no se pudo acceder2")
            return error("no se pudo autenticar correctamente")
        
        #Cambiamos el token cada que se haga una petición para mayor seuridad
        todays_token()
        return funcion_original(*args, **kwargs)
    

    return funcion_en_segundo_plano

def error(errors):
    return errors