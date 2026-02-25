# Informe de Decisiones de Diseño y Arquitectura

Este documento justifica las decisiones técnicas tomadas para cumplir con los requerimientos de concurrencia, paralelismo y comunicación entre procesos (IPC).

## 1. Asincronismo vs. Multithreading para I/O (Red)
El Servidor Colector utiliza `asyncio` para gestionar las conexiones TCP entrantes de los clientes.
* **Justificación:** La recepción de logs a través de Sockets es una tarea limitada por I/O (I/O Bound). Crear un hilo del sistema operativo (`threading`) por cada cliente conectado generaría un alto consumo de memoria y *context switching*. Al utilizar el Event Loop de `asyncio`, un solo hilo puede gestionar miles de conexiones concurrentes de manera eficiente, leyendo del socket únicamente cuando hay datos disponibles en el buffer.

## 2. Paralelismo (Multiprocessing) para Análisis (CPU)
Para procesar las expresiones regulares (Regex) y detectar las firmas de ataques, se utilizó el módulo `multiprocessing`.
* **Justificación:** El análisis de cadenas complejas es una tarea intensiva de procesador (CPU Bound). En Python, el **GIL (Global Interpreter Lock)** impide que múltiples hilos ejecuten *bytecode* de Python simultáneamente en diferentes núcleos. Al utilizar procesos separados (Pool de Workers), cada proceso cuenta con su propio intérprete y espacio de memoria, logrando paralelismo real y aprovechando arquitecturas multicore.

## 3. Mecanismos de Comunicación IPC
El sistema implementa el patrón de diseño "Productor-Consumidor" mediante `multiprocessing.Queue`. Se utilizan dos colas asíncronas e independientes:
* **`task_queue`:** Desacopla la recepción de red del procesamiento lógico. El Event Loop coloca el log crudo en esta cola en microsegundos, liberando el socket inmediatamente.
* **`result_queue`:** Aísla el procesamiento de la visualización. Los Workers insertan las alertas procesadas aquí, y un proceso independiente (Dashboard) las consume para renderizar la pantalla sin bloquear el análisis.
* **Justificación:** Se optó por `Queue` frente a la memoria compartida (`Value`/`Array` + `Locks`) porque las colas en Python son *process-safe* y manejan la sincronización (semáforos) internamente, mitigando el riesgo de condiciones de carrera y simplificando el diseño.

## 4. Tolerancia a Fallos en Clientes
Los clientes incorporan un mecanismo de reintento de conexión (Retry Loop).
* **Justificación:** En entornos distribuidos y orquestados por contenedores, es común enfrentar problemas de sincronía en el arranque (*Race Conditions*). El bucle asegura que el cliente no se caiga si el servidor tarda más tiempo en levantar, garantizando la resiliencia del sistema.
