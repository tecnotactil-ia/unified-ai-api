# API Routes - Chat Completions (OpenAI Compatible)
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
        
        if not data:
            return jsonify({"error": "No input data provided"}), 400
        
        if 'messages' not in data:
            return jsonify({"error": "Missing 'messages' parameter"}), 400
        
        if 'model' not in data:
            return jsonify({"error": "Missing 'model' parameter"}), 400
        
        model = data.get('model')
        messages = data.get('messages')
        temperature = data.get('temperature', 0.7)
        max_tokens = data.get('max_tokens', 2000)
        stream = data.get('stream', False)
        
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
