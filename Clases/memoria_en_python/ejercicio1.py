import gc

def modificar_lista(list):
    print(f"lista dentro de la funcion antes de modificarla: {list}")
    list.append(10)
    print(f"lista dentro de la funcion despues de modificarla: {list}")


a = [1,2,3,4]
modificar_lista(a)
print(f"lista fuera de la funcion: {a}")

del a
gc.collect()