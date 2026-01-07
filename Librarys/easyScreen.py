from pathlib import Path
ABSOLUTE_PATH =  str(Path(__file__).parent.parent)

if __name__ == "__main__":
    import sys
    sys.path.append(ABSOLUTE_PATH)  # Agregando el area de trabajo al path superior

from Librarys.Librarys import *
import Public.Variables.public as public
from Models.DatosModel import Datos
Global = public.variables

class easyScreen():
    def __init__(self,page):
        self.page : ft.Page = page

    def save_screen_data(self,screen):

        datos = Datos("1")
        print(screen)
        datos.pantalla.set(screen)
        datos.save()
        self.move_to_screen()
    
    def move_to_screen(self):
        datos = Datos("1")
        if datos.pantalla.isEmpty():
            screen = 0
            datos.pantalla.set(screen)
            datos.save()
        else:
            screen = datos.pantalla.get()

        lenMonitors = len(get_monitors())

        if lenMonitors-1 < screen:
            screen = 0

        
        monitores = get_monitors()[screen]
        self.page.window_maximized = False
        self.page.update()
        sleep(.1)

        self.page.window_left = monitores.x
        self.page.window_maximized = True
        self.page.update()

    