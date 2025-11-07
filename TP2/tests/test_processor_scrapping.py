import asyncio
import aiohttp
import time

SERVER_A_URL = "http://127.0.0.1:8080/scrape"

URLS_A_PROBAR = [
    "https://www.python.org",
    "https://www.djangoproject.com/",
    "https://flask.palletsprojects.com/en/3.0.x/",
    "https://www.pygame.org/news",
    "https://fastapi.tiangolo.com/",
    "https://httpbin.org/html",
    "https://realpython.com/",
    "https://pypi.org/project/pytest/",
]

async def fetch_url(session: aiohttp.ClientSession, url: str):
    """Hace una sola petición de scraping."""
    print(f"[Cliente] Iniciando solicitud para: {url}")
    payload = {"url": url}
    
    try:
        start_req = time.monotonic()
        async with session.post(SERVER_A_URL, json=payload, timeout=60) as response:
            data = await response.json()
            end_req = time.monotonic()

            if response.status == 200 and data.get('status') in ('success', 'success_cached'):
                status = data.get('status')
                print(f"[Cliente] ÉXITO ({status}) para: {url} (Tardó: {end_req - start_req:.2f}s)")
                return "OK"
            else:
                print(f"[Cliente] FALLO para: {url} (Status: {response.status}) - {data.get('message')}")
                return "FAIL"
                
    except Exception as e:
        print(f"[Cliente] EXCEPCIÓN para: {url} - {e}")
        return "EXCEPTION"

async def main():
    print("--- Iniciando Stress Test (Prueba de Concurrencia) ---")
    start_total = time.monotonic()
    
    async with aiohttp.ClientSession() as session:
        tasks = []
        for url in URLS_A_PROBAR:
            tasks.append(fetch_url(session, url))
        results = await asyncio.gather(*tasks)
        
    end_total = time.monotonic()
    print("--- Test Finalizado ---")
    print(f"\nResultados: {results.count('OK')} OK, {results.count('FAIL')} Fallos, {results.count('EXCEPTION')} Excepciones.")
    print(f"Número de peticiones: {len(URLS_A_PROBAR)}")
    print(f"Tiempo total: {end_total - start_total:.2f} segundos.")

if __name__ == "__main__":
    asyncio.run(main())