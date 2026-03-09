# Memoria Técnica y Decisiones de Diseño Arquitectónico

Este documento fundamenta las decisiones de ingeniería tomadas para satisfacer los requerimientos de concurrencia, paralelismo, escalabilidad y resiliencia del sistema distribuido.

## 1. Patrón Productor-Consumidor y Message Brokering
Se descartó el uso de colas en memoria pura (`multiprocessing.Queue`) a favor de un intermediario externo (**Redis**).
* **Justificación:** La integración de un Message Broker permite el desacoplamiento estricto entre la capa de red y la capa de cómputo. Provee persistencia y habilita la escalabilidad horizontal de los nodos de procesamiento (Workers).

## 2. Gestión de Red: Concurrencia Asincrónica (I/O-Bound)
El servidor Gateway utiliza la librería `asyncio` para la gestión de Sockets TCP.
* **Justificación:** El modelo tradicional de multihilos (*Thread-per-connection*) genera penalizaciones por *context switching*. El Event Loop de `asyncio` permite gestionar miles de conexiones concurrentes I/O-Bound en un único hilo lógico, maximizando el *throughput*.

## 3. Análisis de Firmas: Paralelismo Real (CPU-Bound)
El motor de expresiones regulares está delegado a **Celery**, utilizando un modelo de concurrencia basado en *prefork*.
* **Justificación:** El análisis léxico masivo es intensivo computacionalmente. Para evadir las limitaciones del *Global Interpreter Lock* (GIL) en CPython, Celery invoca la llamada al sistema `fork()`, instanciando procesos independientes que aprovechan simétricamente todos los núcleos físicos del procesador subyacente (`os.cpu_count()`), lo cual es explícitamente parametrizable.

## 4. Arquitectura Orientada a Eventos y WebSockets (Push vs Pull)
Se sustituyó el mecanismo tradicional de *HTTP Polling* en el Frontend por un modelo reactivo basado en **WebSockets** y el patrón **Publisher/Subscriber (Pub/Sub)** de Redis.

* **Justificación:** El mecanismo de Polling obligaba al cliente a consultar iterativamente el estado del servidor, consumiendo ciclos de CPU y ancho de banda innecesarios, además de introducir latencia artificial. Mediante la integración de `Flask-SocketIO`, el servidor establece una conexión TCP persistente (Full-Duplex) con el navegador. 

Cuando un Worker de Celery identifica una anomalía, actúa como *Publisher* emitiendo un evento en Redis. Un hilo secundario (*Background Thread*) en el backend Flask intercepta el evento como *Subscriber* e instruye al socket a empujar (*Push*) el JSON al cliente. Esto reduce la latencia a milisegundos y desacopla la capa de persistencia de la capa de presentación.

## 5. Parametrización y Configurabilidad
Los módulos principales (`server.py`, `web.py`, `client.py`) implementan la librería `argparse`.
* **Justificación:** Cumplimiento de las buenas prácticas de despliegue en contenedores. Previene el "hardcodeo" de parámetros de red y facilita la orquestación, permitiendo que variables como interfaces de escucha (`0.0.0.0`) y puertos sean inyectados dinámicamente desde el archivo `docker-compose.yml`.