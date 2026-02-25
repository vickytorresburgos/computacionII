import asyncio
import logging
import json
from tasks import process_log_batch 

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')

async def handle_client(reader: asyncio.StreamReader, writer: asyncio.StreamWriter):
    addr = writer.get_extra_info('peername')
    logging.info(f"Conexión TCP aceptada de {addr}")
    try:
        while True:
            data = await reader.readline()
            if not data:
                break
            
            payload = data.decode('utf-8').strip()
            if payload:
                try:
                    log_data = json.loads(payload)
                    cliente_id = log_data.get("cliente_id", "Desconocido")
                    logs = log_data.get("logs", []) 
                    
                    if logs:
                        process_log_batch.delay(cliente_id, logs)
                        logging.info(f"[{cliente_id}] Lote de {len(logs)} logs encolado en Celery.")
                        
                except json.JSONDecodeError:
                    logging.error("Error al decodificar JSON del cliente.")
                    
    except asyncio.CancelledError:
        pass
    finally:
        logging.info(f"Conexión cerrada de {addr}")
        writer.close()
        await writer.wait_closed()

async def main_server(host: str, port: int):
    server = await asyncio.start_server(handle_client, host, port)
    logging.info(f"Servidor Async (Productor) escuchando en {host}:{port}")
    async with server:
        await server.serve_forever()

if __name__ == '__main__':
    HOST, PORT = '0.0.0.0', 8888
    try:
        asyncio.run(main_server(HOST, PORT))
    except KeyboardInterrupt:
        logging.info("Deteniendo servidor TCP...")