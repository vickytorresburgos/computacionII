# Guía de Instalación y Despliegue (SDAS)

Este documento detalla los procedimientos técnicos necesarios para aprovisionar y desplegar el Sistema Distribuido de Análisis de Seguridad (SDAS) en un entorno local utilizando contenedores Docker.

## Prerrequisitos del Sistema
- Sistema Operativo basado en UNIX/Linux recomendado (ej. Ubuntu, Pop!_OS).
- Motor de contenedores **Docker** y orquestador **Docker Compose V2**.
- Intérprete de Python 3.10+ (únicamente para la generación de datos de prueba en el host).

## Fases de Despliegue

### 1. Clonación del Repositorio
Obtenga el código fuente del sistema en su entorno local:
```bash
git clone git@github.com:vickytorresburgos/computacionII.git
cd final
```

### 2. Aprovisionamiento de Datos (Mocking)

El sistema requiere archivos de logs preexistentes para que los agentes clientes comiencen la ingesta de datos. Ejecute el script generador de tráfico para aprovisionar los volúmenes locales:

```bash
python3 generar_logs.py
```

*Nota: Este script generará automáticamente los archivos `logs_locales/web.log` y `logs_locales/db.log` poblados con tráfico HTTP estándar e inyecciones maliciosas simuladas.*

### 3. Orquestación y Levantamiento de Servicios

El sistema consta de una arquitectura de microservicios. Para construir las imágenes e inicializar la topología de red virtual, ejecute:

```bash
docker compose up --build
```

El orquestador gestionará las dependencias de inicio mediante *Healthchecks*, levantando secuencialmente Redis, el Gateway TCP, los Workers de Celery, el servidor Web y, finalmente, los Agentes.

### 4. Acceso a la Interfaz Gráfica

Una vez que la salida estándar (stdout) indique que los servicios están en ejecución, acceda al Dashboard de monitorización a través de un navegador web en:
`http://localhost:5000`
