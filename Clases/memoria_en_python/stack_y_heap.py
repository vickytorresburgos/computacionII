def stack_example():
    a = 10
    b = "holaaaa"

    print(f"id de 'a': {id(a)}")
    print(f"id de 'b': {id(b)}")

def heap_example():
    lista_1 = [1,2,3,4,5]
    print(f"id de 'lista_1': {id(lista_1)}")


stack_example()
heap_example()