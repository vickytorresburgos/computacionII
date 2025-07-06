import multiprocessing
from analizador import analizador_frecuencia, analizador_presion, analizador_oxigeno
from verificador import verificador
from generador import SimpleDataGenerator
import os

def main():
    if os.path.exists("blockchain.json"):
        os.remove("blockchain.json")

if __name__ == "__main__":
    # 1. Crear generador y canales de comunicación
    generator = SimpleDataGenerator()
    generator.create_communication_channels(3)
    child_conns = generator.get_child_connections()

    queue_frec = multiprocessing.Queue()
    queue_pres = multiprocessing.Queue()
    queue_oxi  = multiprocessing.Queue()
    stop_event = multiprocessing.Event()

    # 2. Lanzar procesos analizadores con los pipes correctos
    proc_frec = multiprocessing.Process(target=analizador_frecuencia, args=(child_conns[0], queue_frec, stop_event))
    proc_pres = multiprocessing.Process(target=analizador_presion, args=(child_conns[1], queue_pres, stop_event))
    proc_oxi  = multiprocessing.Process(target=analizador_oxigeno, args=(child_conns[2], queue_oxi, stop_event))

    proc_verif = multiprocessing.Process(target=verificador, args=(queue_frec, queue_pres, queue_oxi, stop_event))

    proc_frec.start()
    proc_pres.start()
    proc_oxi.start()
    proc_verif.start()

    # 3. Generar y enviar datos (esto usa los parent_conn internos del generador)
    generator.start_generation(test_mode=False)  # o test_mode=True para pruebas rápidas

    # 4. Limpiar y esperar procesos
    generator.cleanup()
    proc_frec.join()
    proc_pres.join()
    proc_oxi.join()
    stop_event.set()
    proc_verif.join()