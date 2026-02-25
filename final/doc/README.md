# SDAS - Sistema Distribuido de Análisis de Seguridad

SDAS es un motor de detección de intrusiones ligero basado en firmas. Utiliza una arquitectura distribuida donde múltiples "Agentes" monitorean archivos de logs en tiempo real y envían la información a un "Servidor Central" para su procesamiento en paralelo.

## Uso Básico y Simulación

Una vez que el sistema esté corriendo mediante `docker compose up`, verás el **Dashboard de Seguridad** esperando eventos.

### ¿Cómo simular tráfico y ataques?
Abre una segunda terminal en la raíz del proyecto y utiliza el comando `echo` para inyectar líneas de log en el archivo que los clientes están monitoreando (`logs_locales/access.log`).

**1. Simular tráfico normal (No genera alertas):**
```bash
echo "192.168.1.10 - "GET /index.html HTTP/1.1\"" >> logs_locales/access.log
```

**2. Simular un ataque de SQL Injection (Alerta Crítica - Rojo):**

```bash
echo "10.0.0.5 - \"GET /login?user=' OR 1=1 --\"" >> logs_locales/access.log
```

```bash
echo "192.168.0.1 - \"GET /?id=1 UNION SELECT password FROM users\"" >> logs_locales/access.log
```
**3. Simular un ataque Path Traversal (Alerta Alta - Amarillo):**

```bash
echo "172.16.0.2 - \"GET /../../etc/passwd\"" >> logs_locales/access.log
```

**4. Simular un ataque Cross-Site Scripting XSS (Alerta Media - Cian):**

```bash
echo "192.168.0.9 - \"GET /?search=<script>alert('XSS')</script>\"" >> logs_locales/access.log
```

### Detener la aplicación

Para apagar el servidor y los clientes de manera segura, presiona `Ctrl + C` en la terminal donde está corriendo Docker.

