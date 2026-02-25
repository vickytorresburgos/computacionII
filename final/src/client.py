import argparse
import socket
import json
import time
import sys

def stream_logs(file_path, host, port, client_id):
    conectado = False
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    
    while not conectado:
        try:
            s.connect((host, port))
            conectado = True
        except ConnectionRefusedError:
            print(f"[{client_id}] Esperando al servidor en {host}:{port}... (Reintentando en 2s)")
            time.sleep(2)
            
    print(f"[{client_id}] Conectado Monitoreando '{file_path}'...")
    
    try:
        with s, open(file_path, 'r') as f:
            f.seek(0, 2) 
            
            while True:
                line = f.readline()
                if not line:
                    time.sleep(0.1)
                    continue
                
                payload = json.dumps({"cliente_id": client_id, "log": line.strip()}) + "\n"
                s.sendall(payload.encode('utf-8'))
                
    except FileNotFoundError:
        print(f"Error: El archivo {file_path} no existe. Por favor, créalo primero.", file=sys.stderr)
    except Exception as e:
        print(f"[{client_id}] Conexión perdida: {e}")

def main():
    parser = argparse.ArgumentParser(description="SDAS Client - Resiliente")
    parser.add_argument("--host", type=str, default="127.0.0.1", help="IP del servidor")
    parser.add_argument("--port", type=int, default=8888, help="Puerto del servidor")
    parser.add_argument("--id", type=str, required=True, help="ID del cliente")
    parser.add_argument("--file", type=str, required=True, help="Ruta del archivo de logs")
    
    args = parser.parse_args()
    stream_logs(args.file, args.host, args.port, args.id)

if __name__ == '__main__':
    main()