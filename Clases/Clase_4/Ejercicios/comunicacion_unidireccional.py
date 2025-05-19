from multiprocessing import Process, Pipe

def hijo(conn):
    print("hijo esperando datos")
    data = conn.recv() # Bloqueante: espera que el padre envíe algo
    print("hijo recibe: ", data)

if __name__ == '__main__':
    parent_conn, child_conn = Pipe() #ambos extremos de lpipe


    # crear proceso hijo
    p = Process(target=hijo, args=(child_conn,))
    p.start()

    # padre envia datos por el pipe
    parent_conn.send("Hola hijo soy tu padre")
    print("mensaje enviado")

    # espera a que el hijo termine
    p.join()