# Guía de Instalación y Ejecución

Sigue estos pasos para desplegar el **Sistema Distribuido de Análisis de Seguridad (SDAS)** utilizando Docker.

## Prerrequisitos

*   **Docker** (versión 20.10+)
*   **Docker Compose** (versión 3.8+)
*   Conectividad a Internet para la descarga de imágenes base.

## Despliegue Rápido

1.  Clone este repositorio o asegúrate de estar en el directorio raíz del proyecto.
2.  Inicie la infraestructura completa en segundo plano:

    ```bash
    docker compose up --build -d
    ```

    *Este comando construirá las imágenes personalizadas para el servidor, los workers, el dashboard y los clientes.*

3.  Verifica que todos los servicios estén en ejecución:

    ```bash
    docker compose ps
    ```

    Deberías ver:
    *   `sdas_redis`: Activo (Healhy).
    *   `sdas_server`: Activo.
    *   `sdas_web`: Activo.
    *   `celery_worker`: 3 instancias activas.
    *   `sdas_client_web` / `sdas_client_db`: Activos enviando logs.

## Acceso al Dashboard

Una vez desplegado, el dashboard web estará disponible en:

**URL:** [http://localhost:5000](http://localhost:5000)

Desde aquí podrás ver las alertas de seguridad (SQL Injection, XSS, Path Traversal) en tiempo real a medida que los agentes procesan los logs.

## Monitoreo de Logs

Si deseas ver el procesamiento interno del sistema, puedes seguir los logs de los workers de Celery:

```bash
docker compose logs -f celery_worker
```

O los logs del servidor de ingesta TCP:

```bash
docker compose logs -f server
```

## Detención del Sistema

Para detener y eliminar todos los contenedores y redes creadas:

```bash
docker compose down
```
