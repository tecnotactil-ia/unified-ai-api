# Unified AI API Gateway

Unified AI API Gateway compatible con OpenAI API que combina modelos locales (Ollama) con DeepSeek como fallback.

## Características

- ✅ Compatible con OpenAI API
- 🤖 Modelos locales con Ollama (Qwen 2.5 7B)
- ☁️ Fallback a DeepSeek
- 🔐 Gestión de API keys
- 📊 Sistema de estadísticas

## Arquitectura

```
                    ┌─────────────────────┐
                    │   bak.tecnotactil.com │
                    │     (Nginx + SSL)     │
                    └──────────┬────────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                  │
     ┌────────▼────────┐               ┌────────▼────────┐
     │   Ollama        │               │   DeepSeek      │
     │   Qwen 2.5 7B   │               │   (Fallback)    │
     └─────────────────┘               └─────────────────┘
```

## Endpoints

| Endpoint | Descripción |
|----------|-------------|
| `POST /v1/chat/completions` | Chat API (OpenAI compatible) |
| `GET /v1/models` | Listar modelos |
| `GET /health` | Health check |
| `POST /api/manager` | Gestión remota |

## Instalación

```bash
git clone https://github.com/tecnotactil-ia/unified-ai-api.git
cd unified-ai-api
chmod +x install-ai-gateway.sh
./install-ai-gateway.sh
```

## Configuración

```bash
cp .env.example .env
# Editar .env con tus API keys
```

## Uso - Chat API

```bash
curl https://tu-dominio/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_API_KEY" \
  -d '{
    "model": "qwen2.5:7b",
    "messages": [{"role": "user", "content": "Hola"}]
  }'
```

## Gestión Remota

```bash
# Crear API key
python remote_manager.py "crea una API key para MiApp"

# Listar keys
python remote_manager.py "lista las API keys"

# Ver estadísticas
python remote_manager.py "dame las estadísticas"

# Ver salud del sistema
python remote_manager.py "dame la salud del sistema"
```

## Licencia

MIT
