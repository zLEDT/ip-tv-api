

class cola():
    


    def __init__(self):
        self._cola = []
        self._order = "asc"
        self._cola.sort(key=lambda x: x[0])
    
    def put(self,obj,priority=0):

        self._cola.append((priority,obj))
        if self._order == "asc":
            self._cola.sort(key=lambda x: x[0])
        else:
            self._cola.sort(key=lambda x: x[0],reverse=True)
        
    def get(self,get_priority = False):
        if len(self._cola)>0:
            obj = self._cola.pop(0)
            if get_priority:
                return obj
            
            return obj[1]
        
        return None

    def order(self,order):
        if order == "asc":
            self._order = order
        elif order == "des":
            self._order = "des"
        else:
           print ("Parametro de ordenamiento incorrecto solo puede ser 'asc' o 'des' y tu ingresaste : "+order)
           print("Se asignara ordenamiento asc por defecto")
           self._order = "asc"
        
    def size(self):
        return len(self._cola)
    
    def count(self,object = None,priority = 0,otherFlags = None):
        
        
        if object != None:
            if otherFlags != None:
                pos = otherFlags[0]
                subObj = otherFlags[1]
                resultados = list(filter(lambda x: x[1][pos] == subObj, self._cola))
            else:
                resultados = list(filter(lambda x: x[1] == object, self._cola))
            
            return resultados
        
        resultados = list(filter(lambda x: x[0] == priority, self._cola))
        # print(resultados)
        return len(resultados)

    def del_objects(self,objects,current_peticion=False):
        if objects == None:
            print("Objects None returning")
            return
        for obj in objects:
            #Si no existe el objeto en la lista, continuamos
            exist = self._cola.count(obj)
            if exist < 1:
                continue     
            #Si la hora de la petición actual es menor a la hora de la peticion a borrrar no la borramos
            # if current_peticion != False:
            #     if current_peticion.get("hour") < obj[1].get("hour"):
            #         continue
                
            self._cola.remove(obj)
    
    def clear(self):
        self._cola.clear()



if __name__ == "__main__":
    #creamos cola
    colaAudios = cola()
    #Ingresamos tipo ordenamiento ascendente o descendente
    colaAudios.order("asc")
    #Ingresamos valores de prueba con su parametro priority
    # colaAudios.put(0,priority=0)
    colaAudios.put(("upd_hab",{"luz":"1","luz2":"1","id":"1"},2),0)
    print( colaAudios.count(object=("upd_hab",{"luz":"1","luz2":"1","id":"1"},2),otherFlags=[2,2]))
    # print(colaAudios.get())
    #Obtenemos cada valor
    
    # while colaAudios.size() > 0:
    #     print(colaAudios.get())

    #con .count se puede obtener cuantos objetos hay en la lista con el valor pasado como parametro
    # print(colaAudios.count(object=3))#En este caso retornara 2 por los anteriores valores que ingresamos
    



