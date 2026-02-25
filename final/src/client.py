import argparse
import socket
import json
import time
import sys

BATCH_SIZE = 50        # Cantidad de logs por bloque
BATCH_TIMEOUT = 1.0    # Tiempo máximo de espera en segundos antes de enviar (Flush)

def stream_logs(file_path, host, port, client_id):
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    conectado = False
    
    while not conectado:
        try:
            s.connect((host, port))
            conectado = True
        except ConnectionRefusedError:
            print(f"[{client_id}] Esperando al servidor en {host}:{port}... (Reintentando en 2s)")
            time.sleep(2)
            
    print(f"[{client_id}] Conectado monitoreando '{file_path}' en bloques...")
    
    try:
        with s, open(file_path, 'r') as f:            
            batch = []
            last_send_time = time.time()
            
            while True:
                line = f.readline()
                
                if line:
                    batch.append(line.strip())
                else:
                    time.sleep(0.1) 
                
                current_time = time.time()
                if len(batch) >= BATCH_SIZE or (len(batch) > 0 and (current_time - last_send_time) >= BATCH_TIMEOUT):
                    payload = json.dumps({"cliente_id": client_id, "logs": batch}) + "\n"
                    s.sendall(payload.encode('utf-8'))
                    print(f"[{client_id}] Bloque de {len(batch)} logs enviado al servidor.")

                    time.sleep(0.3)
                    
                    batch = []
                    last_send_time = time.time()
                    
    except FileNotFoundError:
        print(f"Error: El archivo {file_path} no existe.", file=sys.stderr)
    except Exception as e:
        print(f"[{client_id}] Conexión perdida: {e}")

def main():
    parser = argparse.ArgumentParser(description="SDAS Client - Batching")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="IP del servidor")
    parser.add_argument("--port", type=int, default=8888, help="Puerto del servidor")
    parser.add_argument("--id", type=str, required=True, help="ID del cliente")
    parser.add_argument("--file", type=str, required=True, help="Ruta del archivo de logs")
    
    args = parser.parse_args()
    stream_logs(args.file, args.host, args.port, args.id)

if __name__ == '__main__':
    main()