"""
Funciones auxiliares para el Sistema Biométrico con Blockchain

Este archivo contiene las funciones básicas que usaremos en todo el proyecto.
"""
import hashlib
import json
import datetime
import random
import os
from typing import Dict, Any, List, Optional


def generate_timestamp() -> str:
    """
    Genera un timestamp en formato ISO 8601
    Ejemplo: "2024-01-15T14:30:45.123456"
    """
    return datetime.datetime.now().isoformat()


def generate_biometric_data() -> Dict[str, Any]:
    """
    Genera datos biométricos simulados según las especificaciones del proyecto
    
    Returns:
        Dict con formato:
        {
            "timestamp": "2024-01-15T14:30:45.123456",
            "frecuencia": 120,  # bpm entre 60-180
            "presion": [140, 85],  # [sistólica, diastólica]
            "oxigeno(%)": 96  # porcentaje entre 90-100
        }
    """
    return {
        "timestamp": generate_timestamp(),
        "frecuencia": random.randint(60, 180),
        "presion": [random.randint(110, 180), random.randint(70, 110)],
        "oxigeno(%)": random.randint(90, 100)
    }


def log_message(message: str, level: str = "INFO") -> None:
    """
    Sistema de logging simple para debug
    
    Args:
        message: Mensaje a mostrar
        level: Nivel de log (INFO, WARNING, ERROR)
    """
    timestamp = datetime.datetime.now().strftime("%H:%M:%S")
    print(f"[{timestamp}] {level}: {message}")


def save_json_file(data: Any, filename: str) -> bool:
    """
    Guarda datos en formato JSON
    
    Args:
        data: Datos a guardar
        filename: Nombre del archivo
        
    Returns:
        True si se guardó correctamente, False si hubo error
    """
    try:
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        return True
    except Exception as e:
        log_message(f"Error guardando {filename}: {e}", "ERROR")
        return False


def load_json_file(filename: str) -> Optional[Any]:
    """
    Carga datos desde archivo JSON
    
    Args:
        filename: Nombre del archivo
        
    Returns:
        Datos cargados o None si hubo error
    """
    try:
        with open(filename, 'r', encoding='utf-8') as f:
            return json.load(f)
    except FileNotFoundError:
        log_message(f"Archivo {filename} no encontrado", "WARNING")
        return None
    except Exception as e:
        log_message(f"Error cargando {filename}: {e}", "ERROR")
        return None


def calcular_hash(prev_hash, datos, timestamp):
    bloque_str = str(prev_hash) + str(datos) + str(timestamp)
    return hashlib.sha256(bloque_str.encode()).hexdigest()


def guardar_blockchain(blockchain, filename="blockchain.json"):
    with open(filename, "w") as f:
        json.dump(blockchain, f, indent=2)

def cargar_blockchain(filename="blockchain.json"):
    if not os.path.exists(filename) or os.stat(filename).st_size == 0:
        return []
    with open(filename, "r") as f:
        return json.load(f)


# Constantes del sistema
TOTAL_SAMPLES = 60  # Total de muestras a generar
SAMPLE_INTERVAL = 1  # Intervalo entre muestras en segundos
WINDOW_SIZE = 30   # Tamaño de ventana móvil en segundos

# Tipos de señales biométricas
SIGNAL_TYPES = ["frecuencia", "presion", "oxigeno"]


if __name__ == "__main__":
    # Pruebas básicas del módulo
    print("=== Pruebas de utils.py ===")
    
    # Probar generación de datos
    print("\n1. Generando datos biométricos de prueba:")
    for i in range(3):
        data = generate_biometric_data()
        print(f"   Muestra {i+1}: {data}")
    
    # Probar guardado/carga JSON
    print("\n2. Probando guardado/carga JSON:")
    test_data = {"prueba": "datos de test", "numero": 42}
    if save_json_file(test_data, "test.json"):
        print("Guardado exitoso")
        loaded = load_json_file("test.json")
        if loaded == test_data:
            print("Carga exitosa")
        else:
            print("Error en carga")
    
    print("\n=== Pruebas completadas ===")