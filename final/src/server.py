import asyncio
import logging
import json
import re
import os
from multiprocessing import Process, Queue

logging.getLogger().setLevel(logging.CRITICAL)

PATTERNS = {
    "SQL_Injection": (r"(?i)(SELECT.*FROM|DROP\s+TABLE|UNION\s+SELECT|'\s*OR\s*1=1)", "CRÍTICA", "\033[91m"), # Rojo
    "Path_Traversal": (r"(?i)(\.\./\.\./|/etc/passwd)", "ALTA", "\033[93m"), # Amarillo
    "XSS": (r"(?i)(<script>|javascript:)", "MEDIA", "\033[96m") # Cian
}

def worker_process(task_queue: Queue, result_queue: Queue, worker_name: str):
    while True:
        try:
            data = task_queue.get()
            if data == "STOP":
                break
            
            log_data = json.loads(data)
            cliente_id = log_data.get("cliente_id", "Desconocido")
            log_text = log_data.get("log", "")
            
            for categoria, (patron, severidad, color) in PATTERNS.items():
                if re.search(patron, log_text):
                    alerta = {
                        "cliente_id": cliente_id,
                        "categoria": categoria,
                        "severidad": severidad,
                        "color": color,
                        "log_detectado": log_text
                    }
                    result_queue.put(alerta)
                    break
        except Exception:
            pass

def dashboard_process(result_queue: Queue):
    """Proceso Consumidor: Lee los resultados y actualiza la pantalla"""
    estadisticas = {"SQL_Injection": 0, "Path_Traversal": 0, "XSS": 0}
    total_alertas = 0
    RESET = "\033[0m"
    
    print("\033[92m" + "="*50)
    print("INICIANDO DASHBOARD DE SEGURIDAD SDAS")
    print("="*50 + RESET + "\nEsperando eventos")

    while True:
        try:
            alerta = result_queue.get()
            if alerta == "STOP":
                break
            
            # Actualizamos estadísticas
            cat = alerta['categoria']
            if cat in estadisticas:
                estadisticas[cat] += 1
                total_alertas += 1
            
            # Formateamos la salida en pantalla
            color = alerta['color']
            print(f"\n{color}ALERTA {alerta['severidad']} detectada!{RESET}")
            print(f" ┣ Origen:  {alerta['cliente_id']}")
            print(f" ┣ Tipo:    {alerta['categoria']}")
            print(f" ┗ Payload: {alerta['log_detectado']}")
            
            # Imprimimos el resumen estadístico
            print("-" * 40)
            print(f"TOTAL ALERTAS: {total_alertas} | SQLi: {estadisticas['SQL_Injection']} | Path: {estadisticas['Path_Traversal']} | XSS: {estadisticas['XSS']}")
            print("-" * 40)
            
        except Exception:
            pass

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter, task_queue: Queue):
    try:
        while True:
            data = await reader.readline()
            if not data:
                break
            payload = data.decode('utf-8').strip()
            if payload:
                task_queue.put(payload)
    except asyncio.CancelledError:
        pass
    finally:
        writer.close()
        await writer.wait_closed()

async def main_server(host: str, port: int, task_queue: Queue):
    server = await asyncio.start_server(lambda r, w: handle_client(r, w, task_queue), host, port)
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    HOST, PORT = '0.0.0.0', 8888
    
    # Mecanismos IPC 
    task_queue = Queue()   # Entrada de logs crudos
    result_queue = Queue() # Salida de alertas procesadas
    
    # Proceso Dashboard
    dashboard = Process(target=dashboard_process, args=(result_queue,), name="Dashboard")
    dashboard.start()
    
    # Pool de Workers
    workers = []
    for i in range(3):
        w = Process(target=worker_process, args=(task_queue, result_queue, f"Worker-{i+1}"))
        w.start()
        workers.append(w)
    
    # Servidor Asincrónico 
    try:
        asyncio.run(main_server(HOST, PORT, task_queue))
    except KeyboardInterrupt:
        print("\nDeteniendo sistema...")
        for _ in workers: task_queue.put("STOP")
        result_queue.put("STOP")
        for w in workers: w.join()
        dashboard.join()