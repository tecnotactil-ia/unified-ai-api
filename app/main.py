#!/usr/bin/env python3
"""
Unified AI API Gateway - bak.tecnotactil.com
Compatible con OpenAI API - Ollama local + DeepSeek fallback
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import os
import json
import logging
from datetime import datetime

app = Flask(__name__)
CORS(app)

# Configuración
OLLAMA_URL = os.getenv('OLLAMA_URL', 'http://localhost:11434')
DEEPSEEK_URL = os.getenv('DEEPSEEK_URL', 'https://api.deepseek.com/chat/completions')
DEEPSEEK_API_KEY = os.getenv('DEEPSEEK_API_KEY', '')
ADMIN_API_KEY = os.getenv('ADMIN_API_KEY', '')
KEYS_FILE = "/root/ai-gateway/api_keys.json"

# Logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def verify_api_key():
    """Verificar API key en headers"""
    auth = request.headers.get('Authorization', '')
    if auth.startswith('Bearer '):
        key = auth[7:]
        
        # Admin key siempre funciona
        if key == ADMIN_API_KEY:
            return True
        
        # Verificar en archivo de keys (búsqueda por prefijo)
        if os.path.exists(KEYS_FILE):
            try:
                with open(KEYS_FILE, 'r') as f:
                    keys = json.load(f)
                
                # Buscar key que comience con el prefijo enviado
                for full_key, data in keys.items():
                    if full_key.startswith(key) and data.get('active', False):
                        # Incrementar contador de requests
                        keys[full_key]['requests'] = keys[full_key].get('requests', 0) + 1
                        with open(KEYS_FILE, 'w') as f:
                            json.dump(keys, f, indent=2)
                        return True
            except Exception as e:
                logger.error(f"Error verificando key: {e}")
    return False

@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status": "healthy",
        "service": "Unified AI API Gateway",
        "domain": "bak.tecnotactil.com"
    })

@app.route('/v1/models', methods=['GET'])
def list_models():
    try:
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
    
    models.extend([
        {"id": "deepseek-chat", "object": "model", "created": 0, "owned_by": "deepseek"},
        {"id": "deepseek-coder", "object": "model", "created": 0, "owned_by": "deepseek"},
        {"id": "deepseek-reasoner", "object": "model", "created": 0, "owned_by": "deepseek"}
    ])
    
    return jsonify({"object": "list", "data": models})

@app.route('/v1/chat/completions', methods=['POST'])
def chat_completions():
    if not verify_api_key():
        return jsonify({"error": "Invalid API key"}), 401
    
    data = request.json
    model = data.get('model', 'qwen2.5:7b')
    messages = data.get('messages', [])
    temperature = data.get('temperature', 0.7)
    max_tokens = data.get('max_tokens', 2000)
    
    logger.info(f"Request: model={model}, messages={len(messages)}")
    
    use_local = True
    model_lower = model.lower()
    
    if 'deepseek' in model_lower or 'reasoner' in model_lower or 'coder' in model_lower:
        use_local = False
    
    if use_local:
        try:
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
            use_local = False
    
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
