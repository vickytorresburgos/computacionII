# SDAS - Sistema Distribuido de Análisis de Seguridad

Este repositorio contiene el **Sistema Distribuido de Análisis de Seguridad (SDAS)**, un proyecto integrador desarrollado para la materia **Computación II**. El sistema implementa una arquitectura robusta y escalable para el monitoreo y detección de intrusiones en tiempo real a través del análisis de logs.

## Visión General

SDAS es un IDS (Intrusion Detection System) distribuido que recolecta logs de múltiples agentes remotos, los procesa de manera paralela mediante una cola de tareas distribuida y visualiza las amenazas detectadas en un dashboard web reactivo.

## Características Principales

*   **Ingesta Asincrónica**: Servidor Gateway basado en `asyncio` para manejar cientos de conexiones TCP concurrentes con baja latencia.
*   **Procesamiento Distribuido**: Motor de análisis basado en **Celery** con workers escalables horizontalmente.
*   **Comunicación de Tiempo Real**: Notificaciones instantáneas al Dashboard mediante **Server-Sent Events (SSE)** sobre Redis Pub/Sub.
*   **Arquitectura de Red Moderna**: Soporte nativo para **IPv6** y Dual Stack (IPv4/IPv6) en todos los componentes.
*   **Control de Concurrencia**: Servidor web multi-hilo con gestión de recursos mediante **Semáforos** y **Locks**.
*   **Eficiencia de Transmisión**: Clientes con lógica de **Batching** para optimizar el uso del ancho de banda.

## Estructura del Proyecto

*   `src/client.py`: Agente de recolección de logs con streaming de archivos.
*   `src/server.py`: Gateway central de ingesta (Async Producers).
*   `src/tasks.py`: Definición de tareas de análisis (Workers).
*   `src/web.py`: Dashboard web y servidor SSE.
*   `src/templates/`: Interfaz de usuario HTML/JS.

## Documentación

Para más detalles, consulta los siguientes archivos en el directorio `doc/`:

1.  **[INSTALL.md](INSTALL.md)**: Guía de instalación y despliegue con Docker.
2.  **[INFO.md](INFO.md)**: Análisis detallado de decisiones de arquitectura y diseño.
3.  **[TODO.md](TODO.md)**: Roadmap y futuras mejoras del sistema.
