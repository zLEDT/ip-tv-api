from pathlib import Path
ABSOLUTE_PATH =  str(Path(__file__).parent.parent)

if __name__ == "__main__":
    import sys
    sys.path.append(ABSOLUTE_PATH)  # Agregando el area de trabajo al path superior

from Librarys.Librarys import *
import Public.Variables.public as public



class easyImage():
    def __init__(self,path,name):
        """path : especifica la ruta de la imagen ej : Public/Images/perfi.jpeg
        name : especifica el nombre con el que se obtendra la imagen en el dict publico
        """
        self.imageOpened = Image.open(ABSOLUTE_PATH+"/"+path)
        
        self.name = name
        self.resize((self.imageOpened.width,self.imageOpened.height))
    
    def minus(self,num):
        width = int(self.imageOpened.width-num)
        height = int(self.imageOpened.height-num)
        self.resize((width,height))
    
    def plus(self,num):
        width = int(self.imageOpened.width+num)
        height = int(self.imageOpened.height+num)
        self.resize((width,height))

    def icon(self):
        """Guarda la imagen con un tamaño de 50x50px"""
        self.resized = self.imageOpened.resize((50,50))
        self.save()

    def tinyIcon(self):
        """Guarda la imagen con un tamaño de 20x20px"""
        self.resized =self.imageOpened.resize((20,20))
        self.save()
    
    def resize(self,size=(50,50)):
       """Define un tamaño de imagen personalizado"""
       self.resized = self.imageOpened.resize(size)
       self.save()

    def save(self):
        """Guarda la imagen con un nombre para obtener desde el dict public.images!"""
        self.image = ImageTk.PhotoImage(self.resized)
        public.images.update({self.name:self.image})
    
    def getImage(self):
        return public.images.get(self.name)