# Rate Limiting Middleware
from flask import request, jsonify
import time

# Simple in-memory rate limiter
request_times = {}

def check_rate_limit(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get('Authorization', 'anonymous')
        now = time.time()
        window = 60  # 1 minute
        
        if key not in request_times:
            request_times[key] = []
        
        # Remove old requests
        request_times[key] = [t for t in request_times[key] if now - t < window]
        
        # Check limit (100 requests per minute)
        if len(request_times[key]) >= 100:
            return jsonify({"error": "Rate limit exceeded"}), 429
        
        request_times[key].append(now)
        return f(*args, **kwargs)
    return decorated
