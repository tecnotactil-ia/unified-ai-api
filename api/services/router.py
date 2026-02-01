# API Router - Decide entre modelo local o remoto
import requests
import json
import logging
from config.settings import load_config

class AIRouter:
    """Decide qué modelo usar basado en complejidad y disponibilidad"""
    
    def __init__(self):
        self.config = load_config()
        self.ollama_url = self.config.get('OLLAMA_URL', 'http://localhost:11434')
        self.deepseek_url = self.config.get('DEEPSEEK_URL', 'https://api.deepseek.com/chat/completions')
        self.deepseek_key = self.config.get('DEEPSEEK_API_KEY', '')
        
        self.remote_models = ['deepseek', 'reasoner', 'coder']
        self.complexity_threshold = 500
    
    def is_complex_request(self, messages):
        total_chars = sum(len(str(m.get('content', ''))) for m in messages)
        return total_chars > self.complexity_threshold
    
    def is_local_model_available(self, model):
        try:
            response = requests.get(f"{self.ollama_url}/api/tags", timeout=5)
            if response.status_code == 200:
                models = response.json().get('models', [])
                model_names = [m['name'] for m in models]
                return any(model in name for name in model_names)
        except:
            pass
        return False
    
    def route_request(self, model, messages, temperature, max_tokens, stream):
        if any(rm in model.lower() for rm in self.remote_models):
            return self.call_deepseek(model, messages, temperature, max_tokens, stream)
        
        if self.is_complex_request(messages):
            logging.info(f"Solicitud compleja → DeepSeek")
            return self.call_deepseek(model, messages, temperature, max_tokens, stream)
        
        if self.is_local_model_available(model):
            logging.info(f"Modelo local → Ollama ({model})")
            return self.call_ollama(model, messages, temperature, max_tokens, stream)
        
        logging.info(f"Fallback → DeepSeek")
        return self.call_deepseek(model, messages, temperature, max_tokens, stream)
    
    def call_ollama(self, model, messages, temperature, max_tokens, stream):
        ollama_messages = self._convert_to_ollama(messages)
        payload = {
            "model": model,
            "messages": ollama_messages,
            "options": {"temperature": temperature, "num_predict": max_tokens},
            "stream": stream
        }
        
        response = requests.post(f"{self.ollama_url}/api/chat", json=payload, timeout=120)
        
        if response.status_code == 200:
            return self._convert_from_ollama(response.json(), model)
        else:
            return self.call_deepseek(model, messages, temperature, max_tokens, stream)
    
    def call_deepseek(self, model, messages, temperature, max_tokens, stream):
        payload = {
            "model": "deepseek-chat",
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream
        }
        headers = {"Authorization": f"Bearer {self.deepseek_key}", "Content-Type": "application/json"}
        response = requests.post(self.deepseek_url, json=payload, headers=headers, timeout=120)
        
        if response.status_code == 200:
            return response.json()
        else:
            raise Exception(f"DeepSeek API error: {response.status_code}")
    
    def _convert_to_ollama(self, messages):
        ollama_messages = []
        system_prompt = None
        for msg in messages:
            if msg.get('role') == 'system':
                system_prompt = msg.get('content', '')
            else:
                ollama_messages.append({"role": msg.get('role', 'user'), "content": msg.get('content', '')})
        if system_prompt and ollama_messages:
            ollama_messages[0]['content'] = f"{system_prompt}\n\n{ollama_messages[0]['content']}"
        return ollama_messages
    
    def _convert_from_ollama(self, response, original_model):
        return {
            "id": f"chatcmpl-{response.get('id', 'local')}",
            "object": "chat.completion",
            "created": 1234567890,
            "model": original_model,
            "choices": [{
                "index": 0,
                "message": {"role": "assistant", "content": response.get('message', {}).get('content', '')},
                "finish_reason": "stop"
            }],
            "usage": {"prompt_tokens": 0, "completion_tokens": 0, "total_tokens": 0}
        }
