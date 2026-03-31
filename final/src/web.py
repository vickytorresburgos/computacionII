import os
import json
import redis # type: ignore
import argparse
import threading
import socket
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from urllib.parse import urlparse

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)

# Mecanismos de sincronización
MAX_CONCURRENT_STREAMS = 5
stream_semaphore = threading.Semaphore(MAX_CONCURRENT_STREAMS)
clients_lock = threading.Lock()
state = {"active_clients": 0}

class SDASHTTPRequestHandler(BaseHTTPRequestHandler):
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        if parsed_path.path == '/':
            self.serve_index()
        elif parsed_path.path == '/api/alerts':
            self.serve_alerts()
        elif parsed_path.path == '/stream':
            self.serve_stream()
        else:
            self.send_error(404, "Not Found")

    def serve_index(self):
        try:
            template_path = os.path.join(os.path.dirname(__file__), 'templates', 'index.html')
            with open(template_path, 'rb') as file:
                content = file.read()
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(content)
        except FileNotFoundError:
            self.send_error(404, "Template index.html not found")

    def serve_alerts(self):
        try:
            raw_alerts = redis_client.lrange('sdas_alerts', 0, -1)
            alerts = [json.loads(alert) for alert in raw_alerts]
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps(alerts).encode('utf-8'))
        except Exception as e:
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

    def serve_stream(self):
        # Limite de cantidad de conexiones concurrentes usando Semaphore
        if not stream_semaphore.acquire(blocking=False):
            self.send_error(503, "Service Unavailable: Demasiados clientes conectados simultaneamente")
            return
            
        with clients_lock:
            state["active_clients"] += 1
            print(f"Nuevo cliente SSE conectado. Total de hilos consumiendo SSE: {state['active_clients']}")

        self.send_response(200)
        self.send_header('Content-type', 'text/event-stream')
        self.send_header('Cache-Control', 'no-cache')
        self.send_header('Connection', 'keep-alive')
        self.send_header('Access-Control-Allow-Origin', '*')
        self.end_headers()

        pubsub = redis_client.pubsub()
        pubsub.subscribe('sdas_alerts_channel')
        
        try:
            for message in pubsub.listen():
                if message['type'] == 'message':
                    sse_message = f"data: {message['data']}\n\n"
                    self.wfile.write(sse_message.encode('utf-8'))
                    self.wfile.flush()
        except (BrokenPipeError, ConnectionResetError):
            pass
        finally:
            pubsub.unsubscribe('sdas_alerts_channel')
            stream_semaphore.release()
            
            with clients_lock:
                state["active_clients"] -= 1
                print(f"Cliente SSE desconectado. Total limitados por semaforo: {state['active_clients']}")

class DualStackServer(ThreadingHTTPServer):
    address_family: int = int(socket.AF_INET6)
    
    def server_bind(self):
        self.socket.setsockopt(socket.IPPROTO_IPV6, socket.IPV6_V6ONLY, 0)
        super().server_bind()

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="SDAS Web Dashboard")
    parser.add_argument("--host", type=str, default="::", help="Host del dashboard")
    parser.add_argument("--port", type=int, default=5000, help="Puerto del dashboard")
    args = parser.parse_args()

    server_address = (args.host, args.port)
    httpd = DualStackServer(server_address, SDASHTTPRequestHandler)
    print(f"Iniciando servidor HTTP DualStack/Multihilo en http://[{args.host}]:{args.port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        httpd.server_close()