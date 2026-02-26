# Roadmap y Trabajo Futuro (TODO)

Lista estructurada de mejoras arquitectónicas y funcionales propuestas para iteraciones futuras del sistema:

## 1. Seguridad y Criptografía
- **Múltiplex TLS/SSL:** Implementar cifrado de transporte en los Sockets TCP entre los Agentes y el Gateway para mitigar vectores de ataque *Man-in-the-Middle* (MitM) en topologías WAN.
- **Autenticación Mutua:** Integrar un sistema de autenticación basada en certificados (mTLS) o tokens JWT para asegurar que el Gateway rechace *payloads* provenientes de agentes no autorizados.

## 2. Persistencia y Retención de Datos
- **Almacenamiento a Largo Plazo:** Migrar el registro final de alertas desde la estructura volátil de listas de Redis hacia una base de datos documental indexada (ej. Elasticsearch) o relacional (PostgreSQL) para permitir auditorías históricas complejas.
- **Gestión de Punteros de Archivo:** Implementar un mecanismo de *offsets* persistentes en los agentes clientes para que, en caso de interrupción del proceso, el cliente retome la lectura del log exactamente desde el último byte transmitido, evitando duplicación o pérdida de datos.

## 3. Optimización del Motor de Reglas
- **Compilación de Reglas AOT:** Reemplazar el motor `re` nativo de Python por librerías especializadas en coincidencia de patrones de alto rendimiento (ej. Hyperscan o motor RE2 de Google) para soportar volúmenes masivos de reglas sin degradación lineal del rendimiento.

## 4. Evolución de la Interfaz de Usuario
- **Comunicación Bidireccional (WebSockets):** Reemplazar el mecanismo actual de *HTTP Polling* (`setInterval` en JavaScript) por conexiones persistentes mediante WebSockets (`Flask-SocketIO`). Esto reducirá la carga del servidor web y proveerá una topología *Push* real para las notificaciones de alertas en la interfaz gráfica.
