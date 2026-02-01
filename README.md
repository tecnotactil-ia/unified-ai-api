# Unified AI API Gateway

Unified AI API Gateway compatible con OpenAI API que combina modelos locales (Ollama) con DeepSeek como fallback.

## Características

- ✅ Compatible con OpenAI API
- 🤖 Modelos locales con Ollama (Qwen 2.5 7B)
- ☁️ Fallback a DeepSeek
- 🔐 Gestión de API keys
- 📊 Sistema de estadísticas

## Instalación

```bash
# Clonar el repositorio
git clone https://github.com/tecnotactil-ia/unified-ai-api.git
cd unified-ai-api

# Hacer ejecutable el script
chmod +x install-ai-gateway.sh

# Ejecutar instalación
./install-ai-gateway.sh
```

## Configuración

1. Copiar `.env.example` a `.env`:
   ```bash
   cp .env.example .env
   ```

2. Editar `.env` con tus credenciales:
   - `DEEPSEEK_API_KEY`: Tu API key de DeepSeek
   - `ADMIN_API_KEY`: Key de administración

3. Configurar Nginx con SSL

## Uso

### Endpoint principal (OpenAI compatible)

```bash
curl https://tu-dominio/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_API_KEY" \
  -d '{
    "model": "qwen2.5:7b",
    "messages": [{"role": "user", "content": "Hola"}]
  }'
```

### Ver modelos disponibles

```bash
curl https://tu-dominio/v1/models
```

## Gestión Remota

Sistema de gestión mediante comandos:

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

## Estructura

```
unified-ai-api/
├── install-ai-gateway.sh    # Script de instalación
├── remote_manager.py        # Gestión remota
├── app/
│   └── api_manager.py       # Gestor de APIs
├── .env.example             # Plantilla de configuración
├── docker-compose.yml       # Orquestación Docker
└── README.md
```

## Arquitectura

```
                    ┌─────────────────────┐
                    │   bak.tecnotactil.com │
                    │     (Nginx + SSL)     │
                    └──────────┬────────────┘
                               │
                    ┌──────────▼────────────┐
                    │   Unified AI Gateway   │
                    │   (Puerto 8080)        │
                    └──────────┬────────────┘
                               │
              ┌────────────────┴────────────────┐
              │                                  │
     ┌────────▼────────┐               ┌────────▼────────┐
     │   Ollama        │               │   DeepSeek      │
     │   Qwen 2.5 7B   │               │   (Fallback)    │
     │   (Local)       │               │                 │
     └─────────────────┘               └─────────────────┘
```

## Servicios

| Servicio | Puerto | Descripción |
|----------|--------|-------------|
| API Gateway | 8080 | Endpoint principal |
| Manager | 8081 | Gestión remota |

## Licencia

MIT

## Autor

[tecnotactil-ia](https://github.com/tecnotactil-ia)
