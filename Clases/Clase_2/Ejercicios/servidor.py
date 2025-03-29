import os
import time

def atender(cliente_id):
    print(f"atendiendo cliente numero: {cliente_id} (pid: {os.getpid()})")
    time.sleep(2)
    print(f"cliente: {cliente_id} atendido")

for i in range(5):
    pid = os.fork()
    if pid == 0:
        atender(i+1)
        exit(0)

for _ in range(5):
    os.wait()

print("todos los clientes fueron atendidos")