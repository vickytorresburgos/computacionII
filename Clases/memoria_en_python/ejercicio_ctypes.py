import ctypes

c_float = ctypes.c_float(1.25)
puntero_float = ctypes.pointer(c_float)

print(f"valor inicial del numero: {puntero_float.contents.value}")

puntero_float.contents.value = 6.25

print(f"nuevo valor del numero: {puntero_float.contents.value}")
print(f"valor original del numero: {c_float.value}")