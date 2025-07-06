import time
import numpy as np

def analizador_frecuencia(pipe_in, queue_out, stop_event):
    ventana = []
    while not stop_event.is_set():
        try:
            data = pipe_in.recv()
            if data is None:
                break
        except EOFError:
            break
        ventana.append(data["frecuencia"])
        if len(ventana) > 30:
            ventana.pop(0)
        media = np.mean(ventana)
        desv = np.std(ventana)
        print(f"[ANALIZADOR:FRECUENCIA] {data['timestamp']} | media: {media:6.2f} | desv: {desv:6.2f}")
        queue_out.put({
            "tipo": "frecuencia",
            "timestamp": data["timestamp"],
            "media": media,
            "desv": desv
        })
        time.sleep(1)

def analizador_presion(pipe_in, queue_out, stop_event):
    ventana = []
    while not stop_event.is_set():
        try:
            data = pipe_in.recv()
            if data is None:
                break
        except EOFError:
            break
        ventana.append(data["presion"])
        if len(ventana) > 30:
            ventana.pop(0)
        media = np.mean(ventana, axis=0)
        desv = np.std(ventana, axis=0)
        media_fmt = [f"{v:.2f}" for v in media]
        desv_fmt = [f"{v:.2f}" for v in desv]
        print(f"[ANALIZADOR:PRESION]    {data['timestamp']} | media: {media_fmt} | desv: {desv_fmt}")
        queue_out.put({
            "tipo": "presion",
            "timestamp": data["timestamp"],
            "media": media.tolist(),
            "desv": desv.tolist()
        })
        time.sleep(1)

def analizador_oxigeno(pipe_in, queue_out, stop_event):
    ventana = []
    while not stop_event.is_set():
        try:
            data = pipe_in.recv()
            if data is None:
                break
        except EOFError:
            break
        ventana.append(data["oxigeno(%)"])
        if len(ventana) > 30:
            ventana.pop(0)
        media = np.mean(ventana)
        desv = np.std(ventana)
        print(f"[ANALIZADOR:OXIGENO]    {data['timestamp']} | media: {media:6.2f} | desv: {desv:6.2f}")
        queue_out.put({
            "tipo": "oxigeno",
            "timestamp": data["timestamp"],
            "media": media,
            "desv": desv
        })
        time.sleep(1)