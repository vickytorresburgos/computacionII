import os

read_fd, write_fd = os.pipe()

os.write(write_fd, b"Hola desde el pipe") #os.write necesita bytes

output = os.read(read_fd, 1024) # lee hasta 1024 bytes

print("mensaje recibido: ")

os.close(write_fd)
os.close(read_fd)