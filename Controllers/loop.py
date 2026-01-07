from Librarys.Librarys import threading

def loop(funcion_original):
    def funcion_en_segundo_plano(*args, **kwargs):
        # print(f"Antes de llamar al método {funcion_original.__name__}")
        thread = threading.Thread(target=lambda:funcion_original(*args, **kwargs),daemon=True).start()
        # print(f"Después de llamar al método {funcion_original.__name__}")

    return funcion_en_segundo_plano
