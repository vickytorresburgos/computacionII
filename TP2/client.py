import requests
import json
import sys
import time

SERVER_A_URL = "http://127.0.0.1:8080/scrape"

def test_url(url_to_scrape: str):
    """
    Envía una solicitud de scraping al Servidor A y muestra la respuesta.
    """
    print("="*50)
    print(f"Solicitando análisis para: {url_to_scrape}")
    print(f"-> Enviando POST a {SERVER_A_URL}...")
    
    payload = {"url": url_to_scrape}
    start_time = time.monotonic()
    
    try:
        response = requests.post(SERVER_A_URL, json=payload, timeout=60)
        
        elapsed = time.monotonic() - start_time
        print(f"\nRespuesta recibida en {elapsed:.2f} segundos.")
        print(f"Status Code HTTP: {response.status_code}")
        print("-"*50)

        try:
            response_data = response.json()
            
            if response_data.get("processing_data", {}).get("screenshot"):
                response_data["processing_data"]["screenshot"] = "[...Base64 Image Data...]"
            
            if response_data.get("processing_data", {}).get("thumbnails"):
                response_data["processing_data"]["thumbnails"] = "[...Base64 Thumbnails...]"

            print(json.dumps(response_data, indent=2, ensure_ascii=False))
            
        except requests.JSONDecodeError:
            print("Error: La respuesta no es un JSON válido.")
            print("Respuesta recibida:")
            print(response.text)
            
    except requests.exceptions.Timeout:
        print("\n" + "="*50)
        print(f"Error: La solicitud al Servidor A excedió el timeout (60s).")
        print("Esto puede pasar si la página es muy pesada o el Servidor B falló.")
    except requests.exceptions.ConnectionError:
        print("\n" + "="*50)
        print(f"Error: No se pudo conectar al Servidor A en {SERVER_A_URL}.")
    except Exception as e:
        print(f"\nOcurrió un error inesperado: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
    else:
        url = "https://example.com" 
        print(f"No se proporcionó URL. Usando URL por defecto: {url}\n")
    
    test_url(url)
    