import gc

class Demo:
    def __del__(self):
        print("objeto eliminado")

obj = Demo()
del obj
gc.collect()