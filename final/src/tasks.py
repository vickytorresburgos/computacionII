import re
import json
import redis
import os
from celery import Celery

# Configuración de Celery apuntando a Redis 
BROKER_URL = os.getenv("CELERY_BROKER_URL", "redis://localhost:6379/0")
app = Celery('sdas_tasks', broker=BROKER_URL)

redis_client = redis.StrictRedis.from_url(BROKER_URL, decode_responses=True)

# diccionario de firmas
PATTERNS = {
    "SQL_Injection": (r"(?i)(SELECT.*FROM|DROP\s+TABLE|UNION\s+SELECT|'\s*OR\s*1=1)", "CRÍTICA", "#dc3545"), # Rojo
    "Path_Traversal": (r"(?i)(\.\./\.\./|/etc/passwd)", "ALTA", "#ffc107"), # Amarillo
    "XSS": (r"(?i)(<script>|javascript:)", "MEDIA", "#fd7e14") # Naranja
}

@app.task(name='tasks.process_log_batch')
def process_log_batch(cliente_id, batch):
    """Esta tarea es ejecutada por los Workers de Celery en segundo plano"""
    alertas_detectadas = 0
    
    for log_text in batch:
        for categoria, (patron, severidad, color) in PATTERNS.items():
            if re.search(patron, log_text):
                alerta = {
                    "cliente_id": cliente_id,
                    "categoria": categoria,
                    "severidad": severidad,
                    "color": color,
                    "log_detectado": log_text
                }
                
                # Guarda la alerta en Redis
                redis_client.lpush('sdas_alerts', json.dumps(alerta))
                redis_client.ltrim('sdas_alerts', 0, 99)
                
                alertas_detectadas += 1
                break # Si ya detectó un ataque en esta línea, deja de evaluar otras firmas
                
    return f"Lote procesado: {len(batch)} logs. Alertas encontradas: {alertas_detectadas}"