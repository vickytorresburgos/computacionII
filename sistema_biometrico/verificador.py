import multiprocessing
from utils import calcular_hash, guardar_blockchain, cargar_blockchain

def verificador(queue_frec, queue_pres, queue_oxi, stop_event):
    blockchain = cargar_blockchain()
    prev_hash = blockchain[-1]["hash"] if blockchain else "0"
    bloque_idx = len(blockchain)

    while not stop_event.is_set():
        try:
            # Recibir los tres resultados (puedes usar timeout para evitar bloqueos)
            res_frec = queue_frec.get(timeout=2)
            res_pres = queue_pres.get(timeout=2)
            res_oxi  = queue_oxi.get(timeout=2)
        except Exception:
            break  # Salir si no hay más datos

        # Verificar que los tres resultados tengan el mismo timestamp
        timestamp = res_frec["timestamp"]
        if not (res_pres["timestamp"] == timestamp and res_oxi["timestamp"] == timestamp):
            continue  # Saltar si no coinciden

        # Verificación de rangos
        alerta = (
            res_frec["media"] >= 200 or
            not (90 <= res_oxi["media"] <= 100) or
            res_pres["media"][0] >= 200  # presión sistólica
        )

        datos = {
            "frecuencia": {"media": res_frec["media"], "desv": res_frec["desv"]},
            "presion": {"media": res_pres["media"], "desv": res_pres["desv"]},
            "oxigeno": {"media": res_oxi["media"], "desv": res_oxi["desv"]},
        }

        bloque = {
            "timestamp": timestamp,
            "datos": datos,
            "alerta": alerta,
            "prev_hash": prev_hash,
        }
        bloque["hash"] = calcular_hash(prev_hash, datos, timestamp)

        blockchain.append(bloque)
        guardar_blockchain(blockchain)

        print("-" * 70)
        print(f"[VERIFICADOR] {timestamp} | Bloque {bloque_idx:02d} | alerta: {str(alerta):5} | hash: {bloque['hash'][:8]}...")
        print("-" * 70)
        bloque_idx += 1
        prev_hash = bloque["hash"]