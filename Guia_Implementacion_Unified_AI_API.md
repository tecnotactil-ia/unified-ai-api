# 🚀 Guía de Implementación: Unified AI API Gateway

**Autor:** IAFasioBoy (Asistente IA de Felix Rodríguez Roble)  
**Fecha:** 31 de enero de 2026  
**Email:** felix.roble@tecnotactil.com

---

## 📋 Tabla de Contenido

1. [Visión General](#visión-general)
2. [Arquitectura](#arquitectura)
3. [Requisitos del Servidor](#requisitos-del-servidor)
4. [Instalación de Modelos Locales](#instalación-de-modelos-locales)
5. [Implementación del Proxy API](#implementación-del-proxy-api)
6. [Configuración](#configuración)
7. [Deployment](#deployment)
8. [Uso](#uso)
9. [Mantenimiento](#mantenimiento)

---

## 1. 🎯 Visión General

```
┌─────────────────────────────────────────────────────────────────┐
│                    Unified AI API Gateway                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                 │
│   Cliente (cualquier app)                                       │
│        │                                                        │
│        ▼                                                        │
│   ┌─────────────────────────────────────────────┐              │
│   │  Flask API (puerto 8080)                   │              │
│   │  - Compatible OpenAI格式                    │              │
│   │  - Rate limiting                           │              │
│   │  - Load balancing                          │              │
│   │  - Fallback automático                     │              │
│   └─────────────────────────────────────────────┘              │
│              │                           │                     │
│              ▼                           ▼                     │
│   ┌──────────────────┐        ┌──────────────────┐            │
│   │ Modelos Locales  │        │  DeepSeek API    │            │
│   │ (Ollama/Llama)   │        │  (Fallback)      │            │
│   │ Qwen 7B          │        │  chat/completion │            │
│   │ Llama 3B         │        │                  │            │
│   └──────────────────┘        └──────────────────┘            │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘
```

### Características

- ✅ **Compatible OpenAI API** - Tus apps funcionan igual
- ✅ **Modelos locales gratuitos** - Qwen, Llama, Mistral
- ✅ **Fallback automático** - Si el local falla, usa DeepSeek
- ✅ **Rate limiting** - Control de uso
- ✅ **Logging** - Control de costos

---

## 2. 🏗️ Arquitectura

```
unified-ai-api/
├── api/
│   ├── __init__.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── chat.py          # Endpoint /v1/chat/completions
│   │   ├── models.py        # Endpoint /v1/models
│   │   └── health.py        # Health checks
│   ├── services/
│   │   ├── __init__.py
│   │   ├── local_model.py   # Ollama integration
│   │   ├── remote_model.py  # DeepSeek API
│   │   └── router.py        # Decision engine
│   └── middleware/
│       ├── __init__.py
│       ├── auth.py          # API key validation
│       ├── rate_limit.py    # Rate limiting
│       └── logging.py       # Request/response logging
├── config/
│   ├── __init__.py
│   ├── settings.py          # Configuración principal
│   └── prompts.py           # System prompts
├── tests/
│   └── test_api.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
├── run.py
└── README.md
```

---

## 3. 💻 Requisitos del Servidor

### Servidor Dedicado (recomendado)

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| CPU | 8 núcleos | 12+ núcleos |
| RAM | 16 GB | 24 GB |
| Storage | 100 GB SSD | 500 GB SSD |
| GPU | Opcional | NVIDIA 24GB VRAM |
| Red | 100 Mbps | 1 Gbps |

### Modelos Recomendados según RAM

| RAM Disponible | Modelo Local | Tamaño |
|----------------|--------------|--------|
| 8 GB | Qwen2.5 3B | ~4GB |
| 16 GB | Qwen2.5 7B | ~7GB |
| 24 GB | Qwen2.5 14B | ~14GB |
| 32 GB+ | Qwen2.5 32B | ~32GB |

---

## 4. 🐳 Instalación de Modelos Locales (Ollama)

### Paso 1: Instalar Ollama

```bash
# En el servidor dedicado
curl -fsSL https://ollama.ai/install.sh | sh

# Iniciar servicio
sudo systemctl start ollama
sudo systemctl enable ollama

# Verificar instalación
ollama --version
```

### Paso 2: Descargar Modelos

```bash
# Modelo recomendado para 24GB RAM
ollama pull qwen2.5:7b          # ~7GB - Conversación general

# Modelos adicionales
ollama pull llama3.2:3b         # ~4GB - Chat rápido
ollama pull deepseek-r1:7b      # ~7B - Reasoning
ollama pull mistral:7b          # ~7GB - Balanceado

# Ver modelos instalados
ollama list
```

### Paso 3: Configurar Ollama como API

```bash
# Crear servicio systemd
sudo nano /etc/systemd/system/ollama.service

# Contenido:
[Unit]
Description=Ollama AI Model Server
After=network.target

[Service]
Type=simple
User=ollama
WorkingDirectory=/home/ollama
Environment="OLLAMA_HOST=0.0.0.0:11434"
ExecStart=/usr/local/bin/ollama serve
Restart=always

[Install]
WantedBy=multi-user.target

# Activar
sudo systemctl daemon-reload
sudo systemctl start ollama
sudo systemctl enable ollama
```

---

## 5. 🔧 Implementación del Proxy API

### requirements.txt

```txt
flask>=2.3.0
flask-cors>=4.0.0
gunicorn>=21.0.0
gevent>=23.0.0
requests>=2.31.0
python-dotenv>=1.0.0
redis>=5.0.0
apscheduler>=3.10.0
```

### Archivo Principal: run.py

```python
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
    app.run(host=host, port=port, debug=debug)
```

### Endpoint de Chat: api/routes/chat.py

```python
#!/usr/bin/env python3
"""
API Routes - Chat Completions
Compatible con OpenAI /v1/chat/completions
"""

from flask import Blueprint, request, jsonify
from api.services.router import AIRouter
from api.middleware.auth import require_api_key
from api.middleware.rate_limit import check_rate_limit
import logging

chat_bp = Blueprint('chat', __name__)
router = AIRouter()

@chat_bp.route('/completions', methods=['POST'])
@require_api_key
@check_rate_limit
def create_completion():
    """
    Endpoint compatible con OpenAI Chat Completions
    
    POST /v1/chat/completions
    {
        "model": "qwen2.5:7b",
        "messages": [
            {"role": "system", "content": "Eres un asistente útil."},
            {"role": "user", "content": "Hola, ¿cómo estás?"}
        ],
        "temperature": 0.7,
        "max_tokens": 1000
    }
    """
    try:
        data = request.json
        
        # Validar parámetros requeridos
        if not data:
            return jsonify({"error": "No input data provided"}), 400
        
        if 'messages' not in data:
            return jsonify({"error": "Missing 'messages' parameter"}), 400
        
        if 'model' not in data:
            return jsonify({"error": "Missing 'model' parameter"}), 400
        
        # Extraer parámetros
        model = data.get('model')
        messages = data.get('messages')
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 2000)
        stream = data.get('stream', False)
        
        # Routing: local o remoto
        response = router.route_request(
            model=model,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream
        )
        
        return jsonify(response)
        
    except Exception as e:
        logging.error(f"Error en completions: {e}")
        return jsonify({
            "error": "Internal server error",
            "message": str(e)
        }), 500
```

### Router Inteligente: api/services/router.py

```python
#!/usr/bin/env python3
"""
AI Router - Decide entre modelo local o remoto
"""

import requests
import json
import logging
from config.settings import load_config

class AIRouter:
    """
    Decide qué modelo usar basado en:
    - Complejidad de la tarea
    - Disponibilidad de modelos locales
    - Configuración de fallback
    """
    
    def __init__(self):
        self.config = load_config()
        self.ollama_url = self.config.get('OLLAMA_URL', 'http://localhost:11434')
        self.deepseek_url = self.config.get('DEEPSEEK_URL', 'https://api.deepseek.com/chat/completions')
        self.deepseek_key = self.config.get('DEEPSEEK_API_KEY', '')
        
        # Modelos que van directamente a DeepSeek
        self.remote_models = ['deepseek', 'reasoner', 'coder']
        
        # Umbral de complejidad (chars)
        self.complexity_threshold = 500
    
    def is_complex_request(self, messages):
        """Determina si la solicitud es compleja"""
        total_chars = sum(len(str(m.get('content', ''))) for m in messages)
        return total_chars > self.complexity_threshold
    
    def is_local_model_available(self, model):
        """Verifica si el modelo local está disponible"""
        try:
            response = requests.get(
                f"{self.ollama_url}/api/tags",
                timeout=5
            )
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                return any(model in name for name in model_names)
        except:
            pass
        return False
    
    def route_request(self, model, messages, temperature, max_tokens, stream):
        """
        Rutarea la solicitud al modelo apropiado
        """
        # 1. Si el modelo es explícitamente remoto
        if any(rm in model.lower() for rm in self.remote_models):
            return self.call_deepseek(model, messages, temperature, max_tokens, stream)
        
        # 2. Si es una solicitud compleja → DeepSeek
        if self.is_complex_request(messages):
            logging.info(f"Solicitud compleja detectada → DeepSeek")
            return self.call_deepseek(model, messages, temperature, max_tokens, stream)
        
        # 3. Si el modelo local está disponible → usar local
        if self.is_local_model_available(model):
            logging.info(f"Modelo local disponible → Ollama ({model})")
            return self.call_ollama(model, messages, temperature, max_tokens, stream)
        
        # 4. Fallback a DeepSeek
        logging.info(f"Sin modelo local disponible → Fallback a DeepSeek")
        return self.call_deepseek(model, messages, temperature, max_tokens, stream)
    
    def call_ollama(self, model, messages, temperature, max_tokens, stream):
        """Llama al modelo local vía Ollama"""
        # Convertir mensajes de formato OpenAI a Ollama
        ollama_messages = self._convert_to_ollama(messages)
        
        payload = {
            "model": model,
            "messages": ollama_messages,
            "options": {
                "temperature": temperature,
                "num_predict": max_tokens
            },
            "stream": stream
        }
        
        response = requests.post(
            f"{self.ollama_url}/api/chat",
            json=payload,
            timeout=120
        )
        
        if response.status_code == 200:
            return self._convert_from_ollama(response.json(), model)
        else:
            # Si falla Ollama, fallback a DeepSeek
            logging.warning(f"Ollama falló ({response.status_code}) → Fallback a DeepSeek")
            return self.call_deepseek(model, messages, temperature, max_tokens, stream)
    
    def call_deepseek(self, model, messages, temperature, max_tokens, stream):
        """Llama a DeepSeek API"""
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        
        headers = {
            "Authorization": f"Bearer {self.deepseek_key}",
            "Content-Type": "application/json"
        }
        
        response = requests.post(
            self.deepseek_url,
            json=payload,
            headers=headers,
            timeout=120
        )
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"DeepSeek API error: {response.status_code}")
    
    def _convert_to_ollama(self, messages):
        """Convierte mensajes de OpenAI a formato Ollama"""
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
        
        # Agregar system prompt al primer mensaje si existe
        if system_prompt and ollama_messages:
            ollama_messages[0]['content'] = f"{system_prompt}\n\n{ollama_messages[0]['content']}"
        
        return ollama_messages
    
    def _convert_from_ollama(self, response, original_model):
        """Convierte respuesta de Ollama a formato OpenAI"""
        # Formato simplificado - ajustar según necesidad
        return {
            "id": f"chatcmpl-{response.get('id', 'local')}",
            "object": "chat.completion",
            "created": 1234567890,
            "model": original_model,
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": response.get('message', {}).get('content', '')
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 0,
                "completion_tokens": 0,
                "total_tokens": 0
            }
        }
```

### Middleware de Auth: api/middleware/auth.py

```python
#!/usr/bin/env python3
"""
API Key Authentication
"""

from functools import wraps
from flask import request, jsonify
import os

def get_api_key():
    """Obtiene API key del header o query param"""
    # Header Authorization: Bearer sk-...
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    
    # Query param ?api_key=...
    return request.args.get('api_key', '')

def require_api_key(f):
    """Decorator para requerir API key"""
    @wraps(f)
    def decorated(*args, **kwargs):
        valid_keys = os.environ.get('API_KEYS', '').split(',')
        api_key = get_api_key()
        
        if not api_key or api_key not in valid_keys:
            return jsonify({
                "error": "Invalid or missing API key",
                "message": "Please provide a valid API key"
            }), 401
        
        return f(*args, **kwargs)
    return decorated
```

### Configuración: config/settings.py

```python
#!/usr/bin/env python3
"""
Configuración del sistema
"""

import os
from dotenv import load_dotenv

load_dotenv()

def load_config():
    """Carga configuración desde variables de entorno"""
    return {
        'HOST': os.getenv('HOST', '0.0.0.0'),
        'PORT': int(os.getenv('PORT', 8080)),
        'DEBUG': os.getenv('DEBUG', 'False').lower() == 'true',
        
        # Ollama
        'OLLAMA_URL': os.getenv('OLLAMA_URL', 'http://localhost:11434'),
        
        # DeepSeek
        'DEEPSEEK_URL': os.getenv('DEEPSEEK_URL', 'https://api.deepseek.com/chat/completions'),
        'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY', ''),
        
        # Rate Limiting
        'RATE_LIMIT_REQUESTS': int(os.getenv('RATE_LIMIT_REQUESTS', 100)),
        'RATE_LIMIT_WINDOW': int(os.getenv('RATE_LIMIT_WINDOW', 60)),
        
        # Logging
        'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
    }
```

---

## 6. ⚙️ Configuración

### Archivo .env.example

```bash
# Servidor
HOST=0.0.0.0
PORT=8080
DEBUG=False

# Ollama (modelos locales)
OLLAMA_URL=http://localhost:11434

# DeepSeek API (fallback)
DEEPSEEK_URL=https://api.deepseek.com/chat/completions
DEEPSEEK_API_KEY=sk-tu-api-key-aqui

# API Keys (separadas por coma)
API_KEYS=sk-local-123,sk-production-456

# Rate Limiting
RATE_LIMIT_REQUESTS=100
RATE_LIMIT_WINDOW=60

# Logging
LOG_LEVEL=INFO
```

---

## 7. 🚀 Deployment

### Opción 1: Docker

```bash
# docker-compose.yml
version: '3.8'

services:
  unified-ai-api:
    build: .
    ports:
      - "8080:8080"
    environment:
      - OLLAMA_URL=http://host.ollama:11434
      - DEEPSEEK_API_KEY=${DEEPSEEK_API_KEY}
    depends_on:
      - redis
    networks:
      - ai-network

  redis:
    image: redis:7-alpine
    networks:
      - ai-network

networks:
  ai-network:
    driver: bridge
```

### Opción 2: Systemd

```bash
# /etc/systemd/system/unified-ai-api.service
[Unit]
Description=Unified AI API Gateway
After=network.target ollama.service

[Service]
Type=simple
User=www-data
WorkingDirectory=/opt/unified-ai-api
Environment="PATH=/opt/unified-ai-api/venv/bin"
ExecStart=/opt/unified-ai-api/venv/bin/gunicorn \
    -w 4 \
    -k gevent \
    -b 0.0.0.0:8080 \
    run:app
Restart=always
RestartSec=5

[Install]
WantedBy=multi-user.target
```

### Opción 3: Nginx Reverse Proxy

```nginx
# /etc/nginx/sites-available/ai-api
server {
    listen 80;
    server_name ai-api.tudominio.com;
    
    location / {
        proxy_pass http://127.0.0.1:8080;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
        
        # Timeouts para requests largos
        proxy_connect_timeout 300s;
        proxy_send_timeout 300s;
        proxy_read_timeout 300s;
    }
}
```

---

## 8. 📖 Uso

### Ejemplo con cURL

```bash
# Usar modelo local
curl -X POST http://tu-servidor:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-tu-api-key" \
  -d '{
    "model": "qwen2.5:7b",
    "messages": [
      {"role": "system", "content": "Eres un asistente útil."},
      {"role": "user", "content": "Explicame qué es Python"}
    ],
    "temperature": 0.7
  }'
```

### Ejemplo con Python

```python
import openai

client = openai.OpenAI(
    base_url="http://tu-servidor:8080/v1",
    api_key="sk-tu-api-key"
)

response = client.chat.completions.create(
    model="qwen2.5:7b",
    messages=[
        {"role": "system", "content": "Eres un asistente útil."},
        {"role": "user", "content": "Hola, ¿cómo estás?"}
    ]
)

print(response.choices[0].message.content)
```

### Comparación de Costos

| Escenario | Solo Cloud | Con Proxy Local |
|-----------|------------|-----------------|
| 1000 requests simples | $10-20 USD | $0 USD |
| 1000 requests complejos | $10-20 USD | $10-20 USD |
| Tareas mixtas | $15-25 USD | $5-10 USD |

**Ahorro estimado:** 50-70% en tareas simples

---

## 9. 🛠️ Mantenimiento

### Comandos útiles

```bash
# Ver logs
sudo journalctl -u unified-ai-api -f

# Reiniciar servicio
sudo systemctl restart unified-ai-api

# Verificar estado
sudo systemctl status unified-ai-api

# Actualizar modelo local
ollama pull qwen2.5:7b

# Ver modelos disponibles
ollama list

# Monitorear uso de recursos
htop
```

### Monitoreo

El sistema incluye endpoint de health:

```bash
curl http://tu-servidor:8080/health
```

Respuesta:
```json
{
  "status": "healthy",
  "ollama": "connected",
  "deepseek": "connected",
  "models": ["qwen2.5:7b", "llama3.2:3b"]
}
```

---

## 📊 Resumen de Costos

### Inversión Inicial

| Item | Costo |
|------|-------|
| VPS con 12 núcleos, 24GB RAM | $50-100/mes |
| Dominio | $10-15/año |

### Ahorro Mensual

| Concepto | Antes | Después |
|----------|-------|---------|
| Tokens Cloud | $200-300 | $50-100 |
| **Ahorro** | - | **$150-200/mes** |

**ROI:** 2-3 meses

---

## 📧 Contacto

**Desarrollado por:** IAFasioBoy (Asistente IA de Felix Rodríguez Roble)  
**Email:** felix.roble@tecnotactil.com  
**Fecha:** 31 de enero de 2026

---

## ✅ Próximos Pasos

1. [ ] Obtener VPS con 12 núcleos, 24GB RAM
2. [ ] Instalar Ollama y modelos
3. [ ] Desplegar Unified AI API
4. [ ] Configurar dominio y SSL
5. [ ] Migrar aplicaciones existentes

---

¿Deseas que proceda con la implementación completa o necesitas más detalles en alguna sección específica?
