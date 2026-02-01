#!/usr/bin/env python3
"""
Unified AI API Gateway
Compatible con OpenAI API - Puede usar modelos locales o remotos
"""

from flask import Flask, jsonify, request
from flask_cors import CORS
from api.routes.chat import chat_bp
from api.routes.models import models_bp
from api.routes.health import health_bp
from config.settings import load_config

app = Flask(__name__)
CORS(app)

# Cargar configuración
config = load_config()

# Registrar blueprints
app.register_blueprint(health_bp, url_prefix='/health')
app.register_blueprint(models_bp, url_prefix='/v1')
app.register_blueprint(chat_bp, url_prefix='/v1/chat')

@app.errorhandler(404)
def not_found(e):
    return jsonify({"error": "Not found", "message": str(e)}), 404

@app.errorhandler(500)
def server_error(e):
    return jsonify({"error": "Internal server error", "message": str(e)}), 500

if __name__ == '__main__':
    host = config.get('HOST', '0.0.0.0')
    port = config.get('PORT', 8080)
    debug = config.get('DEBUG', False)
    
    print(f"🚀 Unified AI API Gateway iniciado en http://{host}:{port}")
    print(f"📚 Documentación: http://{host}:{port}/health")
    app.run(host=host, port=port, debug=debug)
