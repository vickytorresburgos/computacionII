import random
from datetime import datetime, timedelta

# Configuración
NUM_LOGS_PER_FILE = 2500  
ARCHIVO_WEB = "logs_locales/web.log"
ARCHIVO_DB = "logs_locales/db.log"

# Datos simulados
ips_normales = [f"192.168.1.{i}" for i in range(10, 100)]
ips_atacantes = ["45.33.22.11", "185.10.9.8", "203.0.113.5", "198.51.100.20"]

# Perfil del servidor WEB (Frontend)
rutas_web = ["/index.html", "/about", "/images/logo.png", "/css/style.css"]
ataques_web = [
    "GET /../../../../etc/passwd HTTP/1.1",                        # Path Traversal (Amarillo)
    "GET /?search=<script>alert('XSS')</script> HTTP/1.1"          # XSS (Naranja)
]

# Perfil del servidor DB 
rutas_db = ["/api/users", "/api/data", "/api/config", "/api/status"]
ataques_db = [
    "GET /login?user=' OR 1=1 -- HTTP/1.1",                                 # SQLi (Rojo)
    "GET /productos?id=1 UNION SELECT username, password FROM users HTTP/1.1" # SQLi (Rojo)
]

def generar_linea(rutas, ataques):
    tiempo = datetime.now() - timedelta(minutes=random.randint(0, 60))
    str_tiempo = tiempo.strftime("[%d/%b/%Y:%H:%M:%S +0000]")
    
    es_ataque = random.random() < 0.05 
    
    if es_ataque:
        ip = random.choice(ips_atacantes)
        peticion = random.choice(ataques)
        estado = random.choice([403, 404, 500])
    else:
        ip = random.choice(ips_normales)
        peticion = f"GET {random.choice(rutas)} HTTP/1.1"
        estado = 200
        
    return f"{ip} - - {str_tiempo} \"{peticion}\" {estado}\n"


with open(ARCHIVO_WEB, "a") as f_web, open(ARCHIVO_DB, "a") as f_db:
    for _ in range(NUM_LOGS_PER_FILE):
        f_web.write(generar_linea(rutas_web, ataques_web))
        f_db.write(generar_linea(rutas_db, ataques_db))
        
print("Archivos generados con éxito en la carpeta 'logs_locales/'.")