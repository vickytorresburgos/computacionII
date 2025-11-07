# TP2 - Sistema de Scraping y Análisis Web Distribuido

Este proyecto es una implementación de un sistema distribuido de scraping y análisis web, desarrollado para la materia Computación II.

El sistema utiliza una arquitectura desacoplada con dos servidores principales que se comunican a través de sockets para procesar solicitudes de análisis de URL.

---

## 1. Descripción del Proyecto

El sistema está compuesto por dos componentes principales que se ejecutan de forma independiente:

### Servidor A: Extracción (`server_scraping.py`)

Es la puerta de entrada del sistema. Es un servidor HTTP asíncrono construido con **`aiohttp`** y **`asyncio`**.

* **Rol:** Recibir peticiones HTTP del cliente.
* **Tareas (Asíncronas):**
    1.  Descarga el contenido HTML de una URL (usando `aiohttp`).
    2.  Realiza el scraping de la página (usando `BeautifulSoup`) para extraer título, links, metas, etc.
    3.  Se conecta al Servidor B (vía Sockets) para solicitar el "procesamiento pesado".
    4.  Espera ambas tareas (scraping y procesamiento) de forma concurrente usando `asyncio.gather()`.
    5.  Consolida las respuestas y las devuelve al cliente en formato JSON.
* **Bonus:** Se conecta a **Redis** (usando `redis-py`) para implementar caché y limitación de peticiones (Rate Limiting).

### Servidor B: Procesamiento (`server_processing.py`)

Es el "trabajador pesado" del sistema. Es un servidor de sockets construido con **`socketserver`** y **`multiprocessing`**.

* **Rol:** Escuchar peticiones de trabajo del Servidor A.
* **Tareas (Paralelas):**
    1.  Recibe una URL del Servidor A.
    2.  Utiliza un `ProcessPoolExecutor` para asignar el trabajo a un proceso "worker" (evitando bloquear el GIL).
    3.  El worker usa **`Playwright`** para iniciar un navegador *headless*, tomar un screenshot completo y analizar métricas de rendimiento (sin descargar la página dos veces).
    4.  El worker usa **`Pillow (PIL)`** para generar thumbnails a partir del screenshot.
    5.  Devuelve los resultados (JSON con datos en base64) al Servidor A.

---

## 2. Instrucciones de Instalación

Sigue estos pasos para configurar el entorno.

**1. Crear un Entorno Virtual**:\
Se recomienda un entorno virtual (`venv`) para aislar las dependencias.

```bash
$python3 -m venv env$ source env/bin/activate
````

**2. Instalar Dependencias de Python**: \
Instala todas las librerías necesarias con `pip`:

```bash
(env) $ pip install -r requirements.txt
```

**4. Configurar Redis (Opcional)**
El Servidor A está configurado para usar Redis en `localhost:6379` para caché y rate limiting.

  * Si tienes Redis instalado y corriendo, el servidor se conectará automáticamente.
  * Si **no** tienes Redis, el servidor lo detectará e iniciará en modo "sin caché" (usando `DummyCache`), por lo que no es un requisito estricto para que funcione.

---

## 3\. Instrucciones de Ejecución

Para ejecutar el sistema completo, necesitarás **3 terminales** (todas con el entorno virtual activado: `source env/bin/activate`).

### Terminal 1: Iniciar Servidor B (Procesamiento)

Primero, inicia el servidor de procesamiento, que escuchará en el puerto `9000` y usará 4 procesos worker.

```bash
(env) $ python3 server_processing.py -i 127.0.0.1 -p 9000 -n 4
```

*Verás un log como: `[INFO] Servidor de Procesamiento (B) escuchando en ('127.0.0.1', 9000)`*

### Terminal 2: Iniciar Servidor A (Extracción)

Luego, inicia el servidor de scraping. Le indicamos que escuche en el puerto `8000` y que se conecte al Servidor B en el puerto `9000`.

```bash
(env) $ python3 server_scraping.py -i 127.0.0.1 -p 8000 --proc-ip 127.0.0.1 --proc-port 9000
```

*Verás un log como: `[INFO] Servidor de Scraping (A) listo para correr en http://127.0.0.1:8000`*

### Terminal 3: Ejecutar el Cliente

Finalmente, puedes enviar una solicitud con `client.py`.

**Importante:** Asegúrate de que el archivo `client.py` apunte al puerto correcto (el `8000` del Servidor A).

Ejecuta el cliente:

```bash
(env) $ python3 client.py
```

*(Esto usará `https://example.com` por defecto)*

O prueba una URL específica:

```bash
(env) $ python3 client.py "https://www.python.org/"
```
Aquí tienes una sección de "Testing" lista para agregar a tu `README.md`.

-----

## 4\. Pruebas (Testing)

El proyecto incluye un conjunto de pruebas para verificar el correcto funcionamiento de cada componente de forma aislada y del sistema integrado, como sugiere el enunciado.


### Test de Carga y Concurrencia

Este script es la prueba definitiva del sistema completo. Envía múltiples solicitudes de forma concurrente al Servidor A y mide el tiempo total.

  * **Prueba el Asincronismo (Servidor A):** Verifica que el Servidor A acepta todas las peticiones al instante, sin bloquearse.
  * **Prueba el Paralelismo (Servidor B):** Verifica que el Servidor B procesa las tareas en paralelo. Si 4 tareas de 8 segundos terminan en \~9 segundos (y no en 32), la prueba es exitosa.
  * **Prueba el Caché (Redis):** Si se ejecuta dos veces, la segunda ejecución será casi instantánea (ej: `0.05s`) y el log mostrará `(success_cached)`.

**Para ejecutarlo:**

1.  (Terminal 1) Inicia el `server_processing.py` (con múltiples workers, ej: `-n 4`).
2.  (Terminal 2) Inicia el `server_scraping.py`.
3.  (Terminal 3) Ejecuta el test de carga:
    ```bash
    (env) $ python3 test_processor_scrapping.py
    ```