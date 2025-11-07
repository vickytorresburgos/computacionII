import argparse
import asyncio
import datetime
import logging
from typing import Dict, Any, Tuple
import aiohttp
from aiohttp import web

from common.protocol import send_message_async, recv_message_async
from common.cache import CacheManager
from scraper.html_parser import parse_html

logging.basicConfig(
    level=logging.INFO,
    format="[%(asctime)s] %(levelname)s %(message)s",
)
logger = logging.getLogger("server_scraping")

async def fetch_and_scrape_page(session: aiohttp.ClientSession, url: str) -> Dict[str, Any]:
    """
    Descarga el HTML (I/O-bound) y lo parsea (CPU-bound).
    """
    logger.info(f"[Task 1] Iniciando scraping de {url}")
    try:
        async with session.get(url, timeout=20) as response:
            response.raise_for_status()
            html = await response.text()
            final_url = str(response.url)

            loop = asyncio.get_running_loop()
            scraping_data = await loop.run_in_executor(
                None, parse_html, html, final_url
            )
            
            logger.info(f"[Task 1] Scraping de {url} completado.")
            return scraping_data

    except aiohttp.ClientError as e:
        logger.error(f"[Task 1] Error de HTTP al scrapear {url}: {e}")
        return {"error": f"Error de HTTP: {e}"}
    except asyncio.TimeoutError:
        logger.error(f"[Task 1] Timeout (20s) al scrapear {url}")
        return {"error": "Timeout de 20s alcanzado durante el scraping"}
    except Exception as e:
        logger.error(f"[Task 1] Error inesperado en scraping: {e}")
        return {"error": f"Error de scraping: {str(e)}"}


async def request_processing_heavy(proc_addr: Tuple[str, int], url: str) -> Dict[str, Any]:
    """
    Se conecta al Servidor B (Sockets) y solicita 
    el procesamiento pesado (Playwright, PIL).

    """
    host, port = proc_addr
    logger.info(f"[Task 2] Solicitando procesamiento a Servidor B ({host}:{port}) para {url}")

    async def communicate_with_b():
        """Función interna para aplicar el timeout."""
        reader, writer = await asyncio.open_connection(host, port)
        try:
            request_msg = {"url": url}
            await send_message_async(writer, request_msg)
            response_msg = await recv_message_async(reader)
            return response_msg
        finally:
            writer.close()
            await writer.wait_closed()

    try:
        response_msg = await asyncio.wait_for(communicate_with_b(), timeout=30.0)

        if response_msg and response_msg.get("status") == "success":
            logger.info(f"[Task 2] Procesamiento de {url} completado.")
            return response_msg["data"]
        else:
            error_msg = response_msg.get("message", "Error desconocido del Servidor B")
            logger.error(f"[Task 2] Error del Servidor B: {error_msg}")
            return {"error": error_msg}

    except ConnectionRefusedError:
        logger.error(f"[Task 2] No se pudo conectar al Servidor B en {host}:{port}")
        return {"error": "Servidor de procesamiento (B) no disponible"}
    except asyncio.TimeoutError:
        logger.error(f"[Task 2] Timeout (30s) esperando al Servidor B para {url}")
        return {"error": "Timeout (30s) esperando respuesta del servidor de procesamiento"}
    except Exception as e:
        logger.error(f"[Task 2] Error en comunicación con Servidor B: {e}")
        return {"error": f"Error de socket: {str(e)}"}

async def handle_scrape(request: web.Request):
    """
    Manejador principal de aiohttp. Orquesta todo el proceso.
    """
    try:
        data = await request.json()
        url = data.get("url")
        if not url or not url.startswith(('http://', 'https://')):
            return web.json_response(
                {"status": "error", "message": "Se requiere una 'url' válida (http/https)"},
                status=400
            )
    except Exception:
        return web.json_response(
            {"status": "error", "message": "JSON body inválido"},
            status=400
        )

    logger.info(f"Petición recibida para {url}")

    http_session: aiohttp.ClientSession = request.app['http_session']
    proc_addr: Tuple[str, int] = request.app['proc_addr']
    cache: CacheManager = request.app['cache']
    rate_limit: int = request.app['rate_limit']
    cache_ttl: int = request.app['cache_ttl']

    try:
        if await cache.is_rate_limited(url, limit=rate_limit):
            logger.warning(f"Rate limit excedido para {url}")
            return web.json_response(
                {"status": "error", "message": f"Rate limit excedido ({rate_limit}/min) para este dominio"},
                status=429
            )

        cached_data = await cache.get_cached(url)
        if cached_data:
            logger.info(f"Sirviendo respuesta desde caché para {url}")
            return web.json_response({
                "url": cached_data["url"],
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "scraping_data": cached_data["scraping_data"],
                "processing_data": cached_data["processing_data"],
                "status": "success_cached"
            })

        logger.info(f"Ejecutando tareas concurrentes para {url}")
        results = await asyncio.gather(
            fetch_and_scrape_page(http_session, url),
            request_processing_heavy(proc_addr, url),
            return_exceptions=True
        )

        scraping_data = results[0]
        processing_data = results[1]

        if isinstance(scraping_data, Exception) or scraping_data.get("error"):
            err = str(scraping_data) if isinstance(scraping_data, Exception) else scraping_data.get("error")
            raise Exception(f"Fallo el scraping (Task 1): {err}")

        if isinstance(processing_data, Exception) or processing_data.get("error"):
            err = str(processing_data) if isinstance(processing_data, Exception) else processing_data.get("error")
            raise Exception(f"Fallo el procesamiento (Task 2): {err}")

        final_response_data = {
            "url": url,
            "scraping_data": scraping_data,
            "processing_data": processing_data
        }

        await cache.set_cache(url, final_response_data, ttl=cache_ttl)
        logger.info(f"Respuesta final generada y cacheada para {url}")

        response_body = {
            "url": url,
            "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
            "scraping_data": scraping_data,
            "processing_data": processing_data,
            "status": "success"
        }

        return web.json_response(response_body, status=200)

    except Exception as e:
        logger.error(f"Error fatal procesando {url}: {e}")
        return web.json_response(
            {
                "url": url,
                "timestamp": datetime.datetime.now(datetime.timezone.utc).isoformat(),
                "message": str(e),
                "status": "error"
            },
            status=500
        )

async def on_startup(app: web.Application):
    """Crea los clientes (HTTP y Redis) al iniciar el servidor."""
    timeout = aiohttp.ClientTimeout(total=20)
    app['http_session'] = aiohttp.ClientSession(timeout=timeout)
    logger.info("Sesión aiohttp creada.")

    try:
        cache = CacheManager(
            host=app['redis_host'],
            port=app['redis_port']
        )
        await cache._client.ping()
        app['cache'] = cache
        logger.info(f"Conectado a Redis en {app['redis_host']}:{app['redis_port']}")
    except Exception as e:
        logger.critical(f"ERROR al conectar con Redis: {e}")
        logger.warning("El caché y rate limiting estarán DESACTIVADOS.")


async def on_cleanup(app: web.Application):
    """Cierra las conexiones al apagar el servidor."""
    await app['http_session'].close()
    await app['cache'].close()
    logger.info("Sesión aiohttp y conexión Redis cerradas.")


def parse_args():
    """Parsea los argumentos de línea de comandos."""
    parser = argparse.ArgumentParser(description="Servidor de Scraping Asíncrono (Parte A)")
    parser.add_argument("-i", "--ip", default="127.0.0.1", help="Dirección de escucha (IPv4/IPv6)")
    parser.add_argument("-p", "--port", type=int, default=8080, help="Puerto de escucha")
    parser.add_argument("--proc-ip", required=True, help="IP del servidor de procesamiento (B)")
    parser.add_argument("--proc-port", type=int, required=True, help="Puerto del servidor de procesamiento (B)")
    parser.add_argument("--redis-host", default="localhost", help="Host de Redis")
    parser.add_argument("--redis-port", default=6379, type=int, help="Puerto de Redis")
    parser.add_argument("--ttl", type=int, default=300, help="TTL (segundos) para el caché")
    parser.add_argument("--limit", type=int, default=10, help="Rate limit (req/min) por dominio")
    
    return parser.parse_args()

def main():
    args = parse_args()
    
    app = web.Application()

    app['proc_addr'] = (args.proc_ip, args.proc_port)
    app['redis_host'] = args.redis_host
    app['redis_port'] = args.redis_port
    app['cache_ttl'] = args.ttl
    app['rate_limit'] = args.limit

    app.on_startup.append(on_startup)
    app.on_cleanup.append(on_cleanup)

    app.router.add_post('/scrape', handle_scrape)

    logger.info(f"Servidor de Scraping (A) listo para correr en http://{args.ip}:{args.port}")
    
    try:
        web.run_app(app, host=args.ip, port=args.port, print=None)
    except OSError as e:
        logger.critical(f"Error al iniciar el servidor (¿puerto en uso?): {e}")
    except KeyboardInterrupt:
        logger.warning("\n[A] Servidor detenido por el usuario.")

if __name__ == "__main__":
    main()