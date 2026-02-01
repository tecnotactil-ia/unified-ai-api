#!/usr/bin/env python3
"""
API Gateway Manager - Comandos para gestión remota
Este script recibe comandos y los ejecuta en el sistema
"""

import os
import json
import subprocess
import requests
from datetime import datetime, timedelta

# Configuración
API_GATEWAY_URL = "http://localhost:8080"
API_KEY_FILE = "/root/ai-gateway/api_keys.json"

class APIManager:
    """Gestor de APIs para ejecutar comandos remotos"""
    
    def __init__(self):
        self.keys_file = API_KEY_FILE
        self.stats_file = "/root/ai-gateway/stats.json"
        self.load_keys()
    
    def load_keys(self):
        """Cargar keys desde archivo"""
        if os.path.exists(self.keys_file):
            with open(self.keys_file, 'r') as f:
                self.keys = json.load(f)
        else:
            self.keys = {}
    
    def save_keys(self):
        """Guardar keys"""
        with open(self.keys_file, 'w') as f:
            json.dump(self.keys, f, indent=2)
    
    def create_key(self, name, description="", rate_limit=100):
        """Crear nueva API key"""
        import secrets
        key = f"sk-bak-{secrets.token_hex(16)}"
        self.keys[key] = {
            "name": name,
            "description": description,
            "rate_limit": rate_limit,
            "active": True,
            "created_at": datetime.now().isoformat(),
            "requests": 0,
            "tokens": 0
        }
        self.save_keys()
        return {
            "status": "ok",
            "key": key,
            "name": name,
            "rate_limit": rate_limit
        }
    
    def list_keys(self):
        """Listar todas las keys"""
        result = []
        for key, data in self.keys.items():
            result.append({
                "key": key[:20] + "...",
                "name": data["name"],
                "active": data["active"],
                "requests": data["requests"],
                "created": data["created_at"]
            })
        return {"status": "ok", "keys": result}
    
    def deactivate_key(self, key_prefix):
        """Desactivar una key (por prefijo)"""
        for k in self.keys:
            if k.startswith(key_prefix):
                self.keys[k]["active"] = False
                self.save_keys()
                return {"status": "ok", "key": k[:20] + "..."}
        return {"status": "error", "message": "Key no encontrada"}
    
    def get_stats(self, days=1):
        """Obtener estadísticas"""
        if os.path.exists(self.stats_file):
            with open(self.stats_file, 'r') as f:
                stats = json.load(f)
        else:
            stats = {"total_requests": 0, "daily": {}}
        
        # Calcular totales
        total = stats.get("total_requests", 0)
        
        # Contar keys activas
        active_keys = sum(1 for k, v in self.keys.items() if v.get("active", False))
        
        return {
            "status": "ok",
            "total_requests": total,
            "active_keys": active_keys,
            "total_keys": len(self.keys)
        }
    
    def health_check(self):
        """Verificar salud del sistema"""
        checks = {}
        
        # Check API Gateway
        try:
            r = requests.get(f"{API_GATEWAY_URL}/health", timeout=5)
            checks["api_gateway"] = "OK" if r.status_code == 200 else "ERROR"
        except:
            checks["api_gateway"] = "DOWN"
        
        # Check Ollama
        try:
            r = requests.get(f"{API_GATEWAY_URL}/v1/models", timeout=5)
            checks["ollama"] = "OK" if r.status_code == 200 else "ERROR"
        except:
            checks["ollama"] = "DOWN"
        
        # Check Nginx
        try:
            r = requests.get(f"http://localhost/health", timeout=5)
            checks["nginx"] = "OK" if r.status_code == 200 else "ERROR"
        except:
            checks["nginx"] = "DOWN"
        
        return {"status": "ok", "checks": checks}
    
    def execute(self, command):
        """Ejecutar comando"""
        cmd = command.lower().strip()
        
        if "crea" in cmd and "key" in cmd:
            # Extraer nombre
            parts = cmd.replace("crea", "").replace("key", "").replace("api", "").strip()
            name = parts if parts else "API Key"
            return self.create_key(name)
        
        elif "lista" in cmd or "lista" in cmd:
            return self.list_keys()
        
        elif "estadísticas" in cmd or "stats" in cmd:
            return self.get_stats()
        
        elif "salud" in cmd or "health" in cmd:
            return self.health_check()
        
        elif "desactiva" in cmd or "bloquea" in cmd:
            # Extraer prefijo de key
            parts = cmd.split()
            prefix = parts[-1] if parts else ""
            return self.deactivate_key(prefix)
        
        elif "ayuda" in cmd or "help" in cmd:
            return {
                "status": "ok",
                "commands": [
                    "crea una API key para [nombre]",
                    "lista las API keys",
                    "dame las estadísticas",
                    "dame la salud del sistema",
                    "desactiva [key]",
                    "ayuda"
                ]
            }
        
        else:
            return {
                "status": "error",
                "message": "Comando no reconocido",
                "available_commands": [
                    "crea una API key para [nombre]",
                    "lista las API keys",
                    "dame las estadísticas",
                    "dame la salud del sistema",
                    "desactiva [key]",
                    "ayuda"
                ]
            }

# CLI para ejecutar comandos
if __name__ == "__main__":
    import sys
    
    manager = APIManager()
    
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
        result = manager.execute(command)
        print(json.dumps(result, indent=2))
    else:
        print("Uso: python api_manager.py [comando]")
        print("Ejemplo: python api_manager.py dame las estadísticas")
