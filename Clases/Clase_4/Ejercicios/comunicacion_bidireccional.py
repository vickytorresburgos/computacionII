from multiprocessing import Process, Pipe

def hijo(conn):
    print("[Hijo] Esperando mensaje del padre")
    mensaje = conn.recv()
    print("[Hijo] Recibido: ", mensaje)

    respuesta = f"Hola padre, recibi tu mensaje: '{mensaje}'"
    conn.send(respuesta)
    print("[Hijo] Respuesta enviada")

if __name__ == '__main__':
    parent_conn, child_conn = Pipe()  # duplex=True por defecto

    p = Process(target=hijo, args=(child_conn,))
    p.start()

    parent_conn.send("Hola hijo, ¿me escuchás?")
    print("[Padre] Mensaje enviado")

    respuesta = parent_conn.recv()
    print("[Padre] Respuesta del hijo:", respuesta)

    p.join()