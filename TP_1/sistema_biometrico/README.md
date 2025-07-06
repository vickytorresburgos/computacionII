# Sistema Concurrente de Análisis Biométrico con Cadena de Bloques Local

## Descripción

Este proyecto simula un sistema distribuido que genera, analiza y valida datos biométricos (frecuencia cardíaca, presión arterial y oxígeno en sangre) en tiempo real, utilizando procesos concurrentes y una cadena de bloques local para garantizar la integridad de los resultados.

## Estructura

- **generador.py**: Genera y envía datos biométricos simulados a los analizadores.
- **analizador.py**: Tres analizadores (frecuencia, presión, oxígeno) procesan los datos en paralelo, calculando media y desviación estándar en una ventana móvil.
- **verificador.py**: Recibe los resultados, valida los rangos, detecta alertas y almacena los resultados en una blockchain local (`blockchain.json`).
- **utils.py**: Funciones auxiliares (hash, timestamp, generación de datos, etc).
- **verificar_cadena.py**: Verifica la integridad de la blockchain y genera un reporte final (`reporte.txt`).

## Ejecución


1. **Ejecuta el sistema principal**:
   ```sh
   git clone 
   cd sistema_biometrico
   python3 main.py
   ```

   Esto generará datos, los analizará y almacenará los resultados en la blockchain.

2. **Verifica la integridad y genera el reporte**:
   ```sh
   python3 verificar_cadena.py
   ```

   Esto creará el archivo `reporte.txt` con:
   - Cantidad total de bloques.
   - Número de bloques con alertas.
   - Promedio general de frecuencia, presión y oxígeno.
   - Errores de integridad si los hay.

## Formato del reporte

Ejemplo de `reporte.txt`:
```
Bloques verificados: 60
Alertas detectadas: 1
Promedio frecuencia: 110.23
Promedio presión: [135.45, 85.32]
Promedio oxígeno: 96.78
Integridad de la cadena: OK
```


## Autores

- Nombre: Maria Victoria Torres Burgos
- Carrera: Ingeniería en Informática
- Materia: Computación II
- Legajo: 62092
- Año: 4° 2025

---