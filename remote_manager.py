#!/usr/bin/env python3
"""
IAFasioBoy - Remote Command Manager for bak.tecnotactil.com
Uso: python remote_manager.py "comando"
"""

import os
import requests
import sys
import json

# Configuración
VPS_URL = "https://bak.tecnotactil.com"
MANAGER_ENDPOINT = f"{VPS_URL}/api/manager"
MANAGER_API_KEY = os.getenv('MANAGER_API_KEY', 'h@oy+@0wzkQ!L*S^My[6RnQK(g=-7PdO')

def send_command(command):
    """Enviar comando al VPS"""
    headers = {"X-Manager-API-Key": MANAGER_API_KEY}
    data = {"command": command}
    
    try:
        response = requests.post(MANAGER_ENDPOINT, json=data, headers=headers, timeout=10)
        return response.json()
    except Exception as e:
        return {"error": str(e)}

# Comandos disponibles
COMMANDS = {
    "crea": "crea una API key para [nombre] - Crear nueva key",
    "lista": "lista las API keys - Ver keys activas",
    "stats": "dame las estadísticas - Ver uso del sistema",
    "salud": "dame la salud del sistema - Ver estado general",
    "desactiva": "desactiva [key_prefix] - Bloquear una key",
    "ayuda": "ayuda - Ver este mensaje"
}

if __name__ == "__main__":
    if len(sys.argv) > 1:
        command = " ".join(sys.argv[1:])
        result = send_command(command)
        print(json.dumps(result, indent=2))
    else:
        print("🔧 Comandos disponibles:")
        for cmd, desc in COMMANDS.items():
            print(f"  • {desc}")
