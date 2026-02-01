# Configuration Loader
import os
from dotenv import load_dotenv

load_dotenv()

def load_config():
    return {
        'HOST': os.getenv('HOST', '0.0.0.0'),
        'PORT': int(os.getenv('PORT', 8080)),
        'DEBUG': os.getenv('DEBUG', 'False').lower() == 'true',
        'OLLAMA_URL': os.getenv('OLLAMA_URL', 'http://localhost:11434'),
        'DEEPSEEK_URL': os.getenv('DEEPSEEK_URL', 'https://api.deepseek.com/chat/completions'),
        'DEEPSEEK_API_KEY': os.getenv('DEEPSEEK_API_KEY', ''),
        'RATE_LIMIT_REQUESTS': int(os.getenv('RATE_LIMIT_REQUESTS', 100)),
        'RATE_LIMIT_WINDOW': int(os.getenv('RATE_LIMIT_WINDOW', 60)),
        'LOG_LEVEL': os.getenv('LOG_LEVEL', 'INFO'),
    }
