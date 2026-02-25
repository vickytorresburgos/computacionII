# Mejoras Futuras y Roadmap (TODO)

Lista de características planificadas para escalar y robustecer el sistema en futuras versiones:

## Seguridad y Criptografía
- **TLS/SSL en Sockets:** Encriptar la comunicación TCP entre los Clientes y el Servidor para evitar ataques de *Man-in-the-Middle* (MitM) en redes no confiables.
- **Autenticación de Clientes:** Implementar un sistema de tokens (ej. JWT o API Keys) para que el servidor rechace logs de orígenes no autorizados.

## Almacenamiento y Persistencia
- **Base de Datos:** Migrar la salida de las alertas (actualmente solo impresas en pantalla) a una base de datos relacional (PostgreSQL) o documental (Elasticsearch/MongoDB) para guardar el histórico de ataques.
- **Rotación de Logs:** Implementar un mecanismo en el cliente que soporte la rotación de archivos de log locales (cuando `access.log` es archivado y reemplazado por uno nuevo).

## Rendimiento y Arquitectura
- **Message Broker Externo:** Reemplazar las `multiprocessing.Queue` por un broker de mensajería robusto como **RabbitMQ** o **Kafka** si el sistema requiere escalar a múltiples servidores físicos en clúster.
- **Motor Regex Optimizado:** Utilizar librerías de expresiones regulares compiladas en C o integraciones con motores de alto rendimiento como *Hyperscan* para soportar un volumen masivo de reglas.

## Interfaz de Usuario
- **Web Dashboard Real:** Construir una interfaz gráfica web (frontend) comunicada mediante WebSockets (`FastAPI` o `Flask-SocketIO`) en lugar de depender de la terminal (CLI).

