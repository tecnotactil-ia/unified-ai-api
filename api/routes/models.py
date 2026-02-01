# API Routes - Models List
from flask import Blueprint, jsonify
import requests

models_bp = Blueprint('models', __name__)

@models_bp.route('/models', methods=['GET'])
def list_models():
    """List available models"""
    # Get local models from Ollama
    try:
        response = requests.get('http://localhost:11434/api/tags', timeout=5)
        if response.status_code == 200:
            local_models = response.json().get('models', [])
        else:
            local_models = []
    except:
        local_models = []
    
    # Return model list in OpenAI format
    models = []
    for m in local_models:
        models.append({
            "id": m['name'],
            "object": "model",
            "created": 0,
            "owned_by": "local"
        })
    
    # Add DeepSeek
    models.append({
        "id": "deepseek-chat",
        "object": "model",
        "created": 0,
        "owned_by": "deepseek"
    })
    
    return jsonify({
        "object": "list",
        "data": models
    })
