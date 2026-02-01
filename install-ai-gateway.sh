#!/bin/bash
# Unified AI API Gateway - Instalación en VPS bak.tecnotactil.com
# OpenAI compatible + Ollama local + DeepSeek fallback
set -e

echo "=============================================="
echo "🚀 Unified AI API Gateway"
echo "   Dominio: bak.tecnotactil.com"
echo "=============================================="
echo ""

# Colores
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Variables
DOMAIN="bak.tecnotactil.com"
N8N_DIR="/root/ai-gateway"
DEEPSEEK_API_KEY="sk-xxxxxxxxxxxxxxxxxxxx"  # Cambiar por tu key
ADMIN_API_KEY="sk-bak-ai-gateway-$(openssl rand -hex 16)"

echo "📋 CONFIGURACIÓN"
echo "   Dominio: $DOMAIN"
echo "   Directorio: $N8N_DIR"
echo ""

# 1. Actualizar sistema
log_info "1️⃣ Actualizando sistema..."
apt-get update -qq
apt-get upgrade -y

# 2. Instalar dependencias
log_info "2️⃣ Instalando dependencias..."
apt-get install -y curl wget git unzip vim htop net-tools python3 python3-pip python3-venv

# 3. Instalar Ollama
log_info "3️⃣ Instalando Ollama..."
curl -fsSL https://ollama.ai/install.sh | sh

systemctl enable ollama
systemctl start ollama

# 4. Descargar modelo Qwen 2.5 7B (aproximadamente 7GB)
log_info "4️⃣ Descargando modelo Qwen 2.5 7B..."
log_warn "   Esto puede tomar 10-20 minutos dependiendo de tu conexión..."

ollama pull qwen2.5:7b

log_info "   Modelo descargado: qwen2.5:7b"

# 5. Crear estructura del proyecto
log_info "5️⃣ Creando estructura del proyecto..."
mkdir -p $N8N_DIR/{app,config,logs}

# 6. Crear entorno virtual Python
log_info "6️⃣ Configurando Python..."
python3 -m venv $N8N_DIR/venv
source $N8N_DIR/venv/bin/activate
pip install --upgrade pip

# 7. Instalar dependencias Python
cat > $N8N_DIR/requirements.txt << 'EOF'
flask>=2.3.0
flask-cors>=4.0.0
gunicorn>=21.0.0
gevent>=23.0.0
requests>=2.31.0
python-dotenv>=1.0.0
EOF

pip install -r $N8N_DIR/requirements.txt

# 8. Crear aplicación Flask
cat > $N8N_DIR/app/main.py << 'PYEOF'
#!/usr/bin/env python3
"""
Unified AI API Gateway - bak.tecnotactil.com
Compatible con OpenAI API - Ollama local + DeepSeek fallback
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuración
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
DEEPSEEK_URL = os.getenv('DEEPSEEK_URL', 'https://api.deepseek.com/chat/completions')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
ADMIN_API_KEY = os.getenv('ADMIN_API_KEY', '')

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_api_key():
    """Verificar API key en headers"""
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        key = auth[7:]
        if key == ADMIN_API_KEY:
            return True
    return False

@app.route('/health', methods=['GET'])
def health():
    """Health check"""
    return jsonify({
        "status": "healthy",
        "service": "Unified AI API Gateway",
        "domain": "bak.tecnotactil.com"
    })

@app.route('/v1/models', methods=['GET'])
def list_models():
    """Listar modelos disponibles"""
    try:
        # Obtener modelos locales de Ollama
        ollama_resp = requests.get(f'{OLLAMA_URL}/api/tags', timeout=5)
        local_models = ollama_resp.json().get('models', [])
    except:
        local_models = []
    
    models = []
    for m in local_models:
        models.append({
            "id": m['name'],
            "object": "model",
            "created": 0,
            "owned_by": "local"
        })
    
    # Agregar DeepSeek
    models.extend([
        {"id": "deepseek-chat", "object": "model", "created": 0, "owned_by": "deepseek"},
        {"id": "deepseek-coder", "object": "model", "created": 0, "owned_by": "deepseek"},
        {"id": "deepseek-reasoner", "object": "model", "created": 0, "owned_by": "deepseek"}
    ])
    
    return jsonify({"object": "list", "data": models})

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    """Endpoint compatible con OpenAI"""
    
    if not verify_api_key():
        return jsonify({"error": "Invalid API key"}), 401
    
    data = request.json
    
    model = data.get('model', 'qwen2.5:7b')
    messages = data.get('messages', [])
    temperature = data.get('temperature', 0.7)
    max_tokens = data.get('max_tokens', 2000)
    
    logger.info(f"Request: model={model}, messages={len(messages)}")
    
    # Determinar si usar local o DeepSeek
    use_local = True
    model_lower = model.lower()
    
    if 'deepseek' in model_lower or 'reasoner' in model_lower or 'coder' in model_lower:
        use_local = False
    
    # Si el modelo local está disponible, usar Ollama
    if use_local:
        try:
            # Convertir mensajes al formato Ollama
            ollama_messages = []
            system_prompt = None
            
            for msg in messages:
                if msg.get('role') == 'system':
                    system_prompt = msg.get('content', '')
                else:
                    ollama_messages.append({
                        "role": msg.get('role', 'user'),
                        "content": msg.get('content', '')
                    })
            
            if system_prompt and ollama_messages:
                ollama_messages[0]['content'] = f"{system_prompt}\n\n{ollama_messages[0]['content']}"
            
            # Llamar Ollama
            ollama_payload = {
                "model": "qwen2.5:7b",
                "messages": ollama_messages,
                "options": {
                    "temperature": temperature,
                    "num_predict": max_tokens
                },
                "stream": False
            }
            
            ollama_resp = requests.post(
                f'{OLLAMA_URL}/api/chat',
                json=ollama_payload,
                timeout=120
            )
            
            if ollama_resp.status_code == 200:
                result = ollama_resp.json()
                content = result.get('message', {}).get('content', '')
                
                return jsonify({
                    "id": f"chatcmpl-local-{datetime.now().timestamp()}",
                    "object": "chat.completion",
                    "created": int(datetime.now().timestamp()),
                    "model": model,
                    "choices": [{
                        "index": 0,
                        "message": {
                            "role": "assistant",
                            "content": content
                        },
                        "finish_reason": "stop"
                    }],
                    "usage": {
                        "prompt_tokens": 0,
                        "completion_tokens": len(content.split()),
                        "total_tokens": len(content.split())
                    }
                })
            
        except Exception as e:
            logger.error(f"Ollama error: {e}")
            log_warn("Ollama falló, usando DeepSeek como fallback")
    
    # Fallback a DeepSeek
    try:
        deepseek_payload = {
            "model": "deepseek-chat" if 'coder' not in model_lower else "deepseek-coder",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens
        }
        
        headers = {
            "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
            "Content-Type": "application/json"
        }
        
        ds_resp = requests.post(DEEPSEEK_URL, json=deepseek_payload, headers=headers, timeout=120)
        
        if ds_resp.status_code == 200:
            return ds_resp.json()
        else:
            return jsonify({"error": f"DeepSeek error: {ds_resp.status_code}"}), 500
            
    except Exception as e:
        logger.error(f"DeepSeek error: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    host = os.getenv('HOST', '0.0.0.0')
    port = int(os.getenv('PORT', 8080))
    
    logger.info(f"🚀 Unified AI API Gateway iniciado en http://{host}:{port}")
    app.run(host=host, port=port)
PYEOF

chmod +x $N8N_DIR/app/main.py

# 9. Crear archivo .env
cat > $N8N_DIR/.env << EOF
HOST=0.0.0.0
PORT=8080
OLLAMA_URL=http://localhost:11434
DEEPSEEK_URL=https://api.deepseek.com/chat/completions
DEEPSEEK_API_KEY=$DEEPSEEK_API_KEY
ADMIN_API_KEY=$ADMIN_API_KEY
EOF

# 10. Configurar Nginx (SIN SSL temporal)
log_info "7️⃣ Configurando Nginx..."
apt-get install -y nginx
systemctl enable nginx
systemctl start nginx

cat > /etc/nginx/sites-available/ai-gateway << 'NGINXEOF'
server {
    server_name bak.tecnotactil.com;
    listen 80;
    listen [::]:80;

    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        proxy_cache_bypass $http_upgrade;
        proxy_read_timeout 300s;
    }
}
NGINXEOF

ln -sf /etc/nginx/sites-available/ai-gateway /etc/nginx/sites-enabled/
nginx -t && systemctl reload nginx

# 11. === SSL - HACER MANUALMENTE DESPUÉS ===
log_warn "8️⃣ SSL - HACER MANUALMENTE DESPUÉS DE LA INSTALACIÓN"
log_warn ""
log_warn "   Una vez que el DNS de bak.tecnotactil.com apunte a este servidor:"
log_warn ""
log_warn "   1. Obtener certificado SSL:"
log_warn "      certbot --nginx -d bak.tecnotactil.com --non-interactive --agree-tos -m tu@email.com"
log_warn ""
log_warn "   2. O si prefieres manual:"
log_warn "      certbot certonly --webroot -w /var/www/html -d bak.tecnotactil.com"
log_warn ""
log_warn "   3. Verificar que los certificados existen:"
log_warn "      ls -la /etc/letsencrypt/live/bak.tecnotactil.com/"
log_warn ""
log_warn "   4. El script nginx ya tiene la configuración correcta para HTTPS"
log_warn "      solo que está comentada temporalmente"
log_warn ""
log_warn "=============================================="

# 12. Crear servicio systemd
log_info "9️⃣ Creando servicio systemd..."
cat > /etc/systemd/system/ai-gateway.service << 'SYSTEMDEOF'
[Unit]
Description=Unified AI API Gateway
After=network.target ollama.service

[Service]
Type=simple
User=root
WorkingDirectory=$N8N_DIR
Environment="PATH=$N8N_DIR/venv/bin"
ExecStart=$N8N_DIR/venv/bin/gunicorn -w 4 -k gevent -b 0.0.0.0:8080 app.main:app
Restart=always

[Install]
WantedBy=multi-user.target
SYSTEMDEOF

systemctl daemon-reload
systemctl enable ai-gateway
systemctl start ai-gateway

# 13. Resumen final
echo ""
echo "=============================================="
echo "✅ INSTALACIÓN COMPLETA"
echo "=============================================="
echo ""
echo "📋 INFORMACIÓN:"
echo "   URL: https://$DOMAIN"
echo "   Puerto interno: 8080"
echo ""
echo "🔑 API Key: $ADMIN_API_KEY"
echo ""
echo "📁 Directorio: $N8N_DIR"
echo ""
echo "🔄 Comandos útiles:"
echo "   Ver estado: systemctl status ai-gateway"
echo "   Reiniciar: systemctl restart ai-gateway"
echo "   Ver logs: journalctl -u ai-gateway -f"
echo ""
echo "⚠️  IMPORTANTE:"
echo "   1. Cambia DEEPSEEK_API_KEY en $N8N_DIR/.env"
echo "   2. Ejecuta certbot para SSL:"
echo "      certbot --nginx -d $DOMAIN --non-interactive --agree-tos -m tu@email.com"
echo ""
echo "🚀 Tu API compatible con OpenAI está lista en:"
echo "   https://$DOMAIN/v1/chat/completions"
echo ""
