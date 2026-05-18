# INFO: Decisiones de Diseño y Arquitectura

Este documento detalla las justificaciones técnicas detrás de las decisiones arquitectónicas del **Sistema Distribuido de Análisis de Seguridad (SDAS)**, alineadas con los contenidos de la materia **Computación II**.

---

## 1. Arquitectura de Ingesta Asincrónica (`asyncio`)

**Implementación**: `src/server.py` utiliza `asyncio.start_server` para gestionar el socket TCP.

**Justificación**: 
El servidor central actúa como un "Ingestion Gateway" que debe ser capaz de recibir flujos masivos de logs de múltiples clientes sin bloquearse. En lugar de crear un hilo por cada cliente (lo cual sería ineficiente en memoria), utilizamos un **bucle de eventos (Event Loop)** que permite manejar cientos de conexiones concurrentes de manera no bloqueante. Esto es ideal para tareas **I/O-Bound** como la recepción de datos por red.

---

## 2. Procesamiento Distribuido y Paralelismo (`Celery` + `Redis`)

**Implementación**: `src/tasks.py` define tareas de procesamiento que son ejecutadas por workers de Celery.

**Justificación**: 
El análisis de seguridad mediante expresiones regulares (Regex) es una tarea **CPU-Bound**. Realizar este análisis dentro del servidor de ingesta afectaría negativamente la latencia de red. 
Al delegar el análisis a **Celery**, desacoplamos la ingesta de la computación. Además, Docker Compose nos permite escalar horizontalmente (`replicas: 3`), logrando un verdadero **procesamiento paralelo** distribuido entre múltiples procesos independientes.

---

## 3. Sincronización y Concurrencia en el Dashboard Web

**Implementación**: `src/web.py` utiliza `ThreadingHTTPServer` junto con mecanismos de sincronización de bajo nivel.

**Justificación**: 
El servidor web debe servir archivos estáticos, una API REST de historial y un flujo persistente de **SSE (Server-Sent Events)**. Para evitar que un cliente SSE bloquee a los demás, se utiliza un modelo multihilo.
Se aplicaron los siguientes mecanismos de control:
*   **Semáforos (`MAX_CONCURRENT_STREAMS = 5`)**: Limita la cantidad de hilos simultáneos dedicados a streaming, evitando el agotamiento de recursos del sistema.
*   **Locks (`threading.Lock`)**: Protege el acceso al estado global (conteo de clientes activos) para evitar **Condiciones de Carrera (Race Conditions)** durante la actualización de estadísticas.

---

## 4. Comunicación Inter-Proceso (IPC) y Persistencia

**Implementación**: Uso de **Redis**.

**Justificación**: 
Redis actúa como el pegamento del sistema distribuido:
1.  **Broker de Mensajería**: Intermedia entre el Servidor Async y los Workers.
2.  **Pub/Sub**: Permite que los Workers publiquen alertas instantáneamente hacia el Dashboard Web sin que estos componentes se conozcan entre sí (acoplamiento débil).
3.  **Almacenamiento Volátil**: Se utiliza una lista circular (`LPUSH` + `LTRIM`) para mantener siempre las últimas 100 alertas disponibles para consultas REST, optimizando el uso de memoria.

---

## 5. Soporte Nativo Dual-Stack (IPv4 / IPv6)

**Implementación**: `DualStackServer` en `web.py` y configuración de red en Docker.

**Justificación**: 
Siguiendo las tendencias modernas de redes, el sistema está diseñado para operar en entornos IPv6. El servidor web hace bind a `::` y desactiva el flag `IPV6_V6ONLY` para aceptar tráfico de ambos protocolos de manera transparente. Esto asegura la interoperabilidad en redes mixtas.

---

## 6. Eficiencia en el Transporte (Batching)

**Implementación**: `src/client.py` agrupa logs antes de enviarlos.

**Justificación**: 
Enviar cada línea de log individualmente por red generaría un overhead excesivo de encabezados TCP/IP. El cliente implementa una lógica de **Batching** basada en tamaño (`BATCH_SIZE`) y tiempo (`BATCH_TIMEOUT`), lo cual reduce la cantidad de paquetes enviados y optimiza la carga del servidor Gateway.
