from multiprocessing import Process, Pipe

def lector(salida, texto):
    """Proceso lector: envía el texto al procesador"""
    try:
        salida.send(texto)
        print("[Lector] Frase enviada.")
        salida.close()
    except Exception as e:
        print("[Lector] Error:", e)

def procesador(entrada, salida):
    """Proceso procesador: convierte el texto a mayúsculas"""
    try:
        frase = entrada.recv()
        print("[Procesador] Frase recibida: ", frase)
        frase_procesada = frase.upper()
        salida.send(frase_procesada)
        print("[Procesador] Frase procesada y enviada.")
        entrada.close()
        salida.close()
    except Exception as e:
        print("[Procesador] Error:", e)

def escritor(entrada):
    """Proceso escritor: escribe la frase y muestra resultado"""
    try:
        frase_final = entrada.recv()
        print("[Escritor] Frase final: ", frase_final)
        entrada.close()
    except Exception as e:
        print("[Escritor] Error:", e)

if __name__ == '__main__':
    p1_read, p1_write = Pipe(duplex=False)
    p2_read, p2_write = Pipe(duplex=False)

    frase = input("[Main] Ingresá una frase: ")

    p_lector = Process(target=lector, args=(p1_write, frase))
    p_procesador = Process(target=procesador, args=(p1_read, p2_write))
    p_escritor = Process(target=escritor, args=(p2_read,))

    p_lector.start()
    p_procesador.start()
    p_escritor.start()

    p_lector.join()
    p_procesador.join()
    p_escritor.join()