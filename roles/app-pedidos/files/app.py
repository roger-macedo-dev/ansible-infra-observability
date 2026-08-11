from flask import Flask, jsonify
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
import random
import time

app = Flask(__name__)

# --- Métricas customizadas ---
PEDIDOS_TOTAL = Counter(
    'pedidos_total', 'Total de pedidos processados', ['status']
)
LATENCIA_PEDIDO = Histogram(
    'pedido_duracao_segundos', 'Tempo de processamento de um pedido'
)

@app.route('/pedido')
def criar_pedido():
    inicio = time.time()
    # simula processamento
    time.sleep(random.uniform(0.05, 0.3))
    PEDIDOS_TOTAL.labels(status='sucesso').inc()
    LATENCIA_PEDIDO.observe(time.time() - inicio)
    return jsonify({"status": "pedido criado com sucesso"})

@app.route('/erro')
def simular_erro():
    PEDIDOS_TOTAL.labels(status='erro').inc()
    return jsonify({"status": "erro ao processar pedido"}), 500

@app.route('/metrics')
def metrics():
    return generate_latest(), 200, {'Content-Type': CONTENT_TYPE_LATEST}

@app.route('/')
def health():
    return jsonify({"status": "ok", "app": "api-pedidos"})

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
