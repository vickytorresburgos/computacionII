## ejemplo con fork ##

# import os

# pid = os.fork()

# if pid > 0:
#     print(f"Este es el proceso padre, PID: {os.getpid()}, el proceso hijo es: {pid}")

# else:
#     print(f"Este es el proceso hijo, PID: {os.getpid()}, el proceso padre es: {os.getppid()}")


## ejemplo con exec ##

# import os

# pid = os.fork()

# if pid == 0:
#     os.execlp("ls", "ls", "-l")
# else: 
#     os.wait()  # El padre espera a que el hijo termine

## espera y sincronizacion ##

# import os
# import time

# pid = os.fork()

# if pid == 0:
#     print("soy el proceso hijo, voy a dormir 2 segundos")
#     time.sleep(2)
#     print("hijo finalizado")

# else:
#     print(f"soy el proceso padre esperando al hijo (PID: {pid})")
#     os.wait()
#     print("proceso hijo finalizado, proceso padre sigue ejecutando")

## proceso zombie ##

# import os
# import time

# pid = os.fork()

# if pid == 0:
#     print(f"soy el proceso hijo (PID: {os.getpid()}), termino ahora") # proceso hijo queda zombi porque el proceso padre no ha leido su estado con wait()
#     exit(0)

# else:
#     print(f"soy el padre (PID: {os.getpid()}) y no llamo a wait")
#     time.sleep(5)
#     print("proceso padre finalizado")

## proceso huerfano ##

# import os
# import time

# pid = os.fork()

# if pid > 0:
#     print(f"soy el proceso padre (pid: {os.getpid()} y termino ahora)")
#     exit(0) # proceso padre terminado

# else:
#     time.sleep(3)
#     print(f"soy el proceso hijo (pid: {os.getpid()}), mi nuevo padre es {os.getpid()}")