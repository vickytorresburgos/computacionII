import os
import json
import redis
import argparse
import threading
from flask import Flask, render_template, jsonify
from flask_socketio import SocketIO

app = Flask(__name__)
socketio = SocketIO(app, cors_allowed_origins="*")

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/api/alerts')
def get_alerts():
    """Ruta REST para cargar el historial inicial al abrir la página"""
    try:
        raw_alerts = redis_client.lrange('sdas_alerts', 0, -1)
        alerts = [json.loads(alert) for alert in raw_alerts]
        return jsonify(alerts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

def redis_listener():
    """Hilo en segundo plano: Escucha eventos (Pub/Sub) de Redis y los empuja por WebSocket"""
    pubsub = redis_client.pubsub()
    pubsub.subscribe('sdas_alerts_channel')
    
    for message in pubsub.listen():
        if message['type'] == 'message':
            alerta = json.loads(message['data'])
            socketio.emit('nueva_alerta', alerta)

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description="SDAS Web Dashboard")
    parser.add_argument("--host", type=str, default="0.0.0.0", help="Host del dashboard")
    parser.add_argument("--port", type=int, default=5000, help="Puerto del dashboard")
    args = parser.parse_args()

    thread = threading.Thread(target=redis_listener, daemon=True)
    thread.start()

    socketio.run(app, host=args.host, port=args.port, allow_unsafe_werkzeug=True)