from multiprocessing import Process, Pipe

def persona_a(conn):
    print("[A] Enviando saludo")
    conn.send("Hola como estas?")
    respuesta = conn.recv()
    print("[A] Recibi:", respuesta)
    conn.close()

def persona_b(conn):
    mensaje = conn.recv()
    print("[B] Recibi el mensaje:", mensaje)
    conn.send("Todo bien vos?")
    conn.close()

if __name__ == '__main__':
    conn1, conn2 = Pipe(duplex=True)

    p1 = Process(target=persona_a, args=(conn1,))
    p2 = Process(target=persona_b, args=(conn2,))

    p1.start()
    p2.start()

    p1.join()
    p2.join()
