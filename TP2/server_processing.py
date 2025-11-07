import argparse
import socket
import socketserver
import sys
import logging
import multiprocessing
from concurrent.futures import ProcessPoolExecutor, TimeoutError
from typing import Dict, Any

from common.protocol import send_message, recv_message
from processor.image_processor import generate_thumbnails
from processor.screenshot_performance import take_screenshot_and_performance


logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
)
logger = logging.getLogger("server_processing")


def process_task_worker(url: str) -> Dict[str, Any]:
    """
    Función "worker" que se ejecuta en un proceso separado.
    Consolida las llamadas a Playwright y PIL.
    """
    try:
        logger.info(f"[Worker] Procesando: {url}")
        
        sc_perf_data = take_screenshot_and_performance(url)
        
        screenshot_b64 = sc_perf_data.get("screenshot")
        if not screenshot_b64:
            raise ValueError("Playwright no devolvió un screenshot")
        
        thumbnails = generate_thumbnails(screenshot_b64, sizes=(128, 256))

        result = {
            "screenshot": screenshot_b64,
            "performance": sc_perf_data["performance"],
            "thumbnails": thumbnails,
        }
        return {"status": "success", "data": result}

    except Exception as e:
        logger.error(f"[Worker] Error procesando {url}: {e}")
        return {"status": "error", "message": str(e)}


class TaskRequestHandler(socketserver.BaseRequestHandler):
    """
    Manejador para cada conexión entrante del Servidor A.
    """
    def handle(self):
        conn = self.request 
        pool: ProcessPoolExecutor = self.server.pool
        addr = self.client_address
        url = "URL desconocida"

        try:
            request = recv_message(conn) 
            url = request.get("url")
            if not url:
                raise ValueError("No se proporcionó URL en la solicitud")
                
            logger.info(f"[B] Recibida solicitud desde {addr}: {url}")

            future = pool.submit(process_task_worker, url)
 
            result_msg = future.result(timeout=30) 
            
            send_message(conn, result_msg)
            if result_msg["status"] == "success":
                logger.info(f"[B] Respuesta enviada a {addr} para {url}")
            else:
                logger.error(f"[B] Error procesado para {addr}: {result_msg['message']}")

        except ConnectionError as e:
            logger.warning(f"[B] Conexión perdida con {addr}: {e}")
        except TimeoutError:
            logger.error(f"[B] Timeout (30s) esperando al worker para {url}")
            send_message(conn, {"status": "error", "message": "Timeout interno del Servidor B (30s)"})
        except Exception as e:
            logger.error(f"[B] Error fatal manejando conexión {addr}: {e}")
            try:
                send_message(conn, {"status": "error", "message": f"Error del Servidor B: {e}"})
            except Exception:
                pass 
        finally:
            logger.info(f"[B] Conexión con {addr} cerrada.")


class ProcessingServer(socketserver.ThreadingTCPServer):
    """Servidor TCP que usa hilos y un pool de procesos."""
    allow_reuse_address = True 

    def __init__(self, server_address, RequestHandlerClass, pool):
        super().__init__(server_address, RequestHandlerClass, bind_and_activate=False)
        self.pool = pool
        
        try:
            socket.inet_pton(socket.AF_INET6, server_address[0])
            self.address_family = socket.AF_INET6
        except socket.error:
            self.address_family = socket.AF_INET
        
        try:
            self.server_bind()
            self.server_activate()
        except Exception as e:
            logger.critical(f"Error al vincular el servidor a {server_address}: {e}")
            sys.exit(1)


def main():
    parser = argparse.ArgumentParser(description="Servidor de procesamiento (B)")
    parser.add_argument("-i", "--ip", default="127.0.0.1", help="IP de escucha")
    parser.add_argument("-p", "--port", type=int, default=9000, help="Puerto de escucha")
    parser.add_argument("-n", "--processes", type=int, default=multiprocessing.cpu_count(),
                        help="Número de procesos worker (default: CPUs disponibles)")
    args = parser.parse_args()
    
    logger.info("Asegúrate de haber corrido 'playwright install' antes de iniciar.")
    logger.info(f"Iniciando pool de procesos con {args.processes} workers...")
    
    with ProcessPoolExecutor(max_workers=args.processes) as pool:
        try:
            addr = (args.ip, args.port)
            server = ProcessingServer(addr, TaskRequestHandler, pool)
            
            ip_type = "IPv6" if server.address_family == socket.AF_INET6 else "IPv4"
            logger.info(f"Servidor de Procesamiento (B) escuchando en {addr} ({ip_type})")
            
            server.serve_forever()
            
        except KeyboardInterrupt:
            logger.warning("\n[B] Servidor detenido por el usuario.")
        finally:
            if 'server' in locals():
                server.shutdown() 
                server.server_close() 
            logger.info("Pool de procesos cerrado.")

if __name__ == "__main__":
    main()