from multiprocessing import Process, Pipe

def proceso_a(salida):
    print("[A] Enviando un numero 10")
    salida.send(10)
    salida.close()

def proceso_b(entrada, salida):
    n = entrada.recv()
    print("[B] Recibido: ", n)
    salida.send(n * 2)
    entrada.close()
    salida.close()

def proceso_c(entrada):
    n = entrada.recv()
    print("[C] Resultado final: ", n)
    entrada.close

if __name__ == '__main__':
    a_b_read, a_b_write = Pipe(duplex=False)
    b_c_read, b_c_write = Pipe(duplex=False)
    
    p1 = Process(target=proceso_a, args=(a_b_write,))
    p2 = Process(target=proceso_b, args=(a_b_read, b_c_write))
    p3 = Process(target=proceso_c, args=(b_c_read,))

    p1.start()
    p2.start()
    p3.start()

    p1.join()
    p2.join()
    p3.join()