# API Key Authentication Middleware
from functools import wraps
from flask import request, jsonify
import os

def get_api_key():
    auth_header = request.headers.get('Authorization', '')
    if auth_header.startswith('Bearer '):
        return auth_header[7:]
    return request.args.get('api_key', '')

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        valid_keys = os.environ.get('API_KEYS', '').split(',')
        api_key = get_api_key()
        if not api_key or api_key not in valid_keys:
            return jsonify({"error": "Invalid or missing API key"}), 401
        return f(*args, **kwargs)
    return decorated
