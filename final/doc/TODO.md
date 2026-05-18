# Roadmap y Trabajo Futuro (TODO)

Lista de mejoras propuestas para la evolución del **Sistema Distribuido de Análisis de Seguridad (SDAS)**:

## 1. Seguridad de la Infraestructura
- **Encriptación de Transporte (TLS/SSL)**: Implementar certificados para asegurar las comunicaciones vía Sockets TCP y HTTPS para el Dashboard.
- **Autenticación de Agentes**: Requerir un Token o API Key en `client.py` para validar que los logs provengan de fuentes autorizadas.
- **Control de Acceso (RBAC)**: Añadir una capa de login al dashboard para restringir la visualización de alertas a personal de seguridad.

## 2. Almacenamiento y Análisis Histórico
- **Persistencia en Base de Datos**: Migrar el historial de alertas desde Redis (volátil) hacia una base de datos documental (MongoDB o Elasticsearch) para análisis forense a largo plazo.
- **Búsqueda Avanzada**: Implementar filtros por fecha, severidad y tipo de ataque en la interfaz web.
- **Reportes Automáticos**: Generar resúmenes en PDF con estadísticas de ataques detectados por día/semana.

## 3. Optimización del Motor de Detección
- **Compilación de Regex**: Utilizar librerías de alto rendimiento como `re2` o `hyperscan` para soportar miles de firmas sin degradar el rendimiento.
- **Firmas Dinámicas**: Permitir la actualización de patrones de ataque sin necesidad de reiniciar los workers de Celery (vía Redis o Base de Datos).
- **Detección Basada en ML**: Integrar modelos de Machine Learning para detectar anomalías de comportamiento que no se ajusten a firmas estáticas.

## 4. Escalabilidad y Red
- **Balanceo de Carga**: Implementar un Load Balancer (Nginx/HAProxy) frente al servidor Gateway para distribuir el tráfico entre múltiples instancias asincrónicas.
- **Dashboard Distribuido**: Adaptar el sistema SSE para funcionar correctamente en clústeres de servidores web utilizando el adaptador de Redis para Pub/Sub coordinado.
