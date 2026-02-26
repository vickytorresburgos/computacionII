# Memoria Técnica y Decisiones de Diseño Arquitectónico

Este documento fundamenta las decisiones de ingeniería tomadas para satisfacer los requerimientos de concurrencia, paralelismo, escalabilidad y resiliencia del sistema distribuido.

## 1. Patrón Productor-Consumidor y Message Brokering
Se descartó el uso de colas en memoria (`multiprocessing.Queue`) a favor de un intermediario externo (**Redis**).
* **Justificación:** La integración de un Message Broker permite el desacoplamiento estricto entre la capa de red y la capa de cómputo. Provee persistencia en memoria y habilita la escalabilidad horizontal; es posible añadir N contenedores de *Workers* distribuidos en diferentes nodos físicos sin alterar la lógica del servidor de ingesta.

## 2. Gestión de Red: Concurrencia Asincrónica (I/O-Bound)
El servidor Gateway utiliza la librería `asyncio` para la gestión de Sockets TCP.
* **Justificación:** La recepción de datos a través de la red implica altos tiempos de espera (*latencia I/O*). El modelo tradicional de multihilos (*Thread-per-connection*) genera un consumo exhaustivo de memoria y penalizaciones por *context switching*. El Event Loop de `asyncio` permite gestionar miles de conexiones concurrentes en un único hilo lógico, maximizando el *throughput* de la aplicación.

## 3. Análisis de Firmas: Paralelismo Real (CPU-Bound)
El motor de expresiones regulares está delegado a **Celery**, el cual utiliza un modelo de concurrencia basado en *prefork* (múltiples procesos pesados).
* **Justificación:** El análisis léxico de cadenas masivas es una tarea intensiva computacionalmente. Debido a las limitaciones del *Global Interpreter Lock* (GIL) en CPython, la ejecución multihilo no provee paralelismo real. Celery invoca la llamada al sistema `fork()`, creando instancias independientes del intérprete de Python, lo que permite aprovechar simétricamente todos los núcleos físicos del procesador subyacente (`os.cpu_count()`).

## 4. Optimización de Ancho de Banda (Batching)
Los agentes clientes no transmiten los logs de manera unitaria. Implementan un *buffer* en memoria que se vacía (*flush*) al alcanzar un límite de registros (`BATCH_SIZE`) o un umbral de tiempo (`TIMEOUT`).
* **Justificación:** Disminuye drásticamente el *overhead* asociado a la pila de protocolos TCP/IP (cabeceras de red) y reduce la cantidad de *System Calls* requeridas para la transmisión, optimizando la utilización del ancho de banda y reduciendo la saturación de I/O en el servidor Gateway. 

## 5. Resiliencia y Tolerancia a Fallos
La infraestructura está orquestada considerando el determinismo de inicialización.
* **Justificación:** En entornos orquestados, las condiciones de carrera (*Race Conditions*) durante el arranque son habituales. Se implementaron *Healthchecks* en Docker Compose para garantizar que los nodos consumidores (Celery) y productores (Server) no inicien hasta que el nodo middleware (Redis) informe disponibilidad de puertos. Adicionalmente, los agentes de telemetría incluyen un bucle de retardo (`time.sleep`) post-envío para evitar inanición de red y simular la intercalación concurrente de logs.