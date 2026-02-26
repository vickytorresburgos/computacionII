# SDAS - Sistema Distribuido de Análisis de Seguridad

SDAS es un motor de detección de intrusiones basado en firmas (NIDS/HIDS híbrido) diseñado sobre una arquitectura distribuida orientada a eventos. El sistema procesa flujos continuos de logs en tiempo real para identificar patrones de ataque comunes utilizando expresiones regulares.

## Arquitectura del Sistema

El proyecto implementa el patrón de diseño Productor-Consumidor apoyado en las siguientes tecnologías:
1.  **Agentes (Clientes TCP):** Procesos ligeros que ingieren archivos de logs locales, implementando técnicas de *Batching* para agrupar registros y transmitirlos al servidor central, mitigando el *overhead* de red.
2.  **Gateway Asincrónico (Servidor TCP):** Implementado con `asyncio`, actúa como un nodo receptor altamente concurrente. Su única responsabilidad es encolar los lotes de datos en el Message Broker.
3.  **Message Broker (Redis):** Actúa como middleware de mensajería para persistir las tareas encoladas y almacenar temporalmente los resultados de las alertas.
4.  **Procesamiento Distribuido (Celery):** Un *pool* de *workers* extrae los lotes de Redis y ejecuta el análisis de firmas (CPU-bound) en paralelo, evadiendo el GIL de Python mediante el modelo *prefork*.
5.  **Dashboard de Monitoreo (Flask):** Interfaz web reactiva que consume la API de resultados en Redis mediante técnicas de *HTTP Polling*.

## Firmas de Detección Soportadas
El motor actualmente clasifica y prioriza las siguientes amenazas:
* **SQL Injection (SQLi):** Severidad CRÍTICA. Búsqueda de manipulación de consultas (ej. `UNION SELECT`, `' OR 1=1`).
* **Path Traversal:** Severidad ALTA. Búsqueda de escalamiento de directorios (`../../`) y acceso a archivos sensibles del SO.
* **Cross-Site Scripting (XSS):** Severidad MEDIA. Inyección de etiquetas `<script>` o pseudoprotocolos de ejecución.

## Inyección Manual de Tráfico
Para evaluar la latencia del sistema en tiempo real, se pueden inyectar líneas de log directamente en los archivos montados en los volúmenes, abriendo una terminal paralela en el host:

**Inyección SQL en Base de Datos:**
```bash
echo "10.0.0.5 - - [25/Feb/2026] \"GET /login?user=' OR 1=1 --\" 403" >> logs_locales/db.log
```

**Inyección XSS en Frontend:**

```bash
echo "192.168.1.1 - - [25/Feb/2026] \"GET /?search=<script>alert('XSS')</script>\" 200" >> logs_locales/web.log
```