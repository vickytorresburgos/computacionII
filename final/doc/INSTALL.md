# Guía de Instalación y Despliegue (SDAS)

Este documento detalla los pasos necesarios para desplegar el Sistema Distribuido de Análisis de Seguridad (SDAS) en un entorno local utilizando Docker.

## Prerrequisitos
- Sistema Operativo basado en Linux 
- **Docker** y **Docker Compose V2** instalados.
- Git (para clonar el repositorio).

## Paso 1: Clonar el Repositorio
Abre tu terminal y ejecuta:
```bash
git clone git@github.com:vickytorresburgos/computacionII.git
cd final
```

## Paso 2: Preparar el Entorno

El sistema requiere un archivo local para que los agentes (clientes) puedan leer los logs. Debes crearlo antes de levantar los contenedores:

```bash
mkdir -p logs_locales
touch logs_locales/access.log

```

## Paso 3: Despliegue con Docker Compose

Para construir las imágenes y levantar la arquitectura completa (1 Servidor + 2 Clientes), ejecuta en la raíz del proyecto:

```bash
docker compose up --build

```

*Nota: Si utilizas una versión antigua de Docker, el comando puede ser `docker-compose up --build`.*
El sistema levantará las dependencias en orden y mostrará el Dashboard en la terminal estándar (stdout).




