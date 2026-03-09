# Roadmap y Trabajo Futuro (TODO)

Lista estructurada de mejoras arquitectónicas y funcionales propuestas para iteraciones futuras del sistema:

## 1. Seguridad y Autenticación
- **Múltiplex TLS/SSL:** Implementar cifrado de transporte en los Sockets TCP entre los Agentes y el Gateway, y configurar WSS (WebSocket Secure) para la interfaz web.
- **Autenticación Mutua (mTLS):** Integrar un sistema de autenticación basada en certificados para asegurar que el Gateway rechace *payloads* provenientes de agentes no autorizados.

## 2. Persistencia y Retención de Datos
- **Almacenamiento a Largo Plazo:** Migrar el registro final de alertas desde la estructura volátil de listas de Redis hacia una base de datos documental indexada (ej. Elasticsearch) para permitir auditorías históricas complejas y consultas por rangos temporales.

## 3. Escalabilidad del Frontend
- **Desacoplamiento del Event Loop de WebSockets:** Actualizar la arquitectura de `Flask-SocketIO` para utilizar un *Message Queue* nativo (como RabbitMQ o la integración directa de Redis con SocketIO) en lugar del hilo en segundo plano actual (`threading.Thread`). Esto permitirá escalar horizontalmente el servidor Flask detrás de un balanceador de carga (Load Balancer) sin perder el enrutamiento de los WebSockets.

## 4. Optimización del Motor de Reglas
- **Compilación de Reglas AOT:** Reemplazar el motor `re` nativo de Python por librerías especializadas en coincidencia de patrones de alto rendimiento (ej. Hyperscan o motor RE2) para soportar miles de reglas de firmas sin degradación lineal del rendimiento.