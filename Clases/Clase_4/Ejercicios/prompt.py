import os

read_fd, write_fd = os.pipe() # crea un pipe anonimo y devuelve dos file descriptors

pid = os.fork()

if pid == 0:
    os.close(write_fd)
    r = os.fdopen(read_fd)
    print("hijo leyendo: ", r.read())
    r.close()
else:
    os.close(read_fd)
    w = os.fdopen(write_fd, 'w')
    w.write("Hola hijo\n")
    w.close()
