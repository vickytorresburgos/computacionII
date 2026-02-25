import os
import json
import redis
from flask import Flask, render_template, jsonify

app = Flask(__name__)

REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
redis_client = redis.StrictRedis.from_url(REDIS_URL, decode_responses=True)

@app.route('/')
def index():
    """Ruta principal que sirve la página HTML"""
    return render_template('index.html')

@app.route('/api/alerts')
def get_alerts():
    """API que devuelve las últimas alertas en formato JSON"""
    try:
        raw_alerts = redis_client.lrange('sdas_alerts', 0, -1)
        alerts = [json.loads(alert) for alert in raw_alerts]
        return jsonify(alerts)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)