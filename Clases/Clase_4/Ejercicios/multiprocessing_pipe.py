from multiprocessing import Process, Pipe

def hijo(conn):
    print("Hijo esperando datos")
    data = conn.recv()
    print("hijo recibio: ", data)

if __name__ == '__main__':
    parent_conn, child_conn = Pipe()
    p = Process(target=hijo, args=(child_conn,))
    p.start()

    parent_conn.send("Hola hijo desde el padre")  # Enviamos datos
    p.join()