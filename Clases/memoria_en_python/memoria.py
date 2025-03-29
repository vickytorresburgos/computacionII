import sys

a = "holaaaa"
b = [1,2,3,4,5]
c = [ "a", "b", "c"]
d = {1: "hola",
     2: "como",
     3: "estas"}

print(f"el tamaño de a es: {sys.getsizeof(a)}")
print(f"el tamaño de b es: {sys.getsizeof(b)}")
print(f"el tamaño de c es: {sys.getsizeof(c)}")
print(f"el tamaño de d es: {sys.getsizeof(d)}")
