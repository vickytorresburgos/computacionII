import os
import time

for i in range (4):
    pid = os.fork()
    
    if pid == 0:
        print(f"hijo {i+1} - pid: {os.getpid()}, ppid: {os.getppid()}")
        exit(0)

for _ in range (4):
    os.wait()

print("todos los hijos finalizados")
