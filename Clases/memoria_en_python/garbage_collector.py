import gc

class Demo:
    def __del__(self): # metodo predefinido en python, se llama automaticamente cuando un objeto esta a punto de ser destruido, ocurre generalmente cuando no hay referencias a ese objeto
        print("objeto eliminado")

obj = Demo()
del obj
gc.collect()