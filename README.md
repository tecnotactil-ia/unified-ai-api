# 🚀 Unified AI API Gateway

**Un proxy API unificado que combina modelos locales gratuitos con DeepSeek como fallback, compatible con OpenAI API.**

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue.svg)](https://www.python.org/downloads/)
[![Flask](https://img.shields.io/badge/Flask-2.3-green.svg)](https://flask.palletsprojects.com/)

---

## 📋 Tabla de Contenido

- [🎯 Acerca del Proyecto](#-acerca-del-proyecto)
- [✨ Características](#-características)
- [🏗️ Arquitectura](#-arquitectura)
- [💻 Requisitos](#-requisitos)
- [🚀 Instalación](#-instalación)
- [📖 Documentación](#-documentación)
- [💰 Ahorro de Costos](#-ahorro-de-costos)
- [🤝 Contribución](#-contribución)
- [📄 Licencia](#-licencia)
- [👨‍💻 Autor](#-autor)

---

## 🎯 Acerca del Proyecto

Unified AI API Gateway es una solución de infraestructura de IA que permite:

- **Optimizar costos** usando modelos locales gratuitos para tareas simples
- **Mantener calidad** haciendo fallback automático a DeepSeek para tareas complejas
- **Migración sin cambios** gracias a su compatibilidad con OpenAI API
- **Control total** sobre el uso de recursos y costos

Este proyecto forma parte de una estrategia de **optimización de costos de IA** para aplicaciones en producción.

### El Problema

```
┌─────────────────────────────────────────────────────────────┐
│  PREGUNTA: "¿Qué es Python?"                                 │
│                                                             │
│  Opción A: DeepSeek (Cloud)                                 │
│  Costo: $0.0001 por request                                 │
│  Tiempo: ~2 segundos                                        │
│                                                             │
│  Opción B: Qwen 7B (Local)                                  │
│  Costo: $0 (gratuito)                                       │
│  Tiempo: ~0.5 segundos                                      │
│                                                             │
│  ⬆️ El 80% de las preguntas son simples                     │
│  ⬆️ Ahorro potencial: 60-80% en costos                      │
└─────────────────────────────────────────────────────────────┘
```

### La Solución

```
┌─────────────────────────────────────────────────────────────┐
│                    Unified AI API Gateway                    │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│   ┌──────────────┐    ┌──────────────┐    ┌──────────────┐ │
│   │   Cliente    │───▶│    Router    │───▶│  Modelo      │ │
│   │  (cualquier  │    │  Inteligente │    │  Local       │ │
│   │   app)       │    │              │    │ (Qwen/Llama) │ │
│   └──────────────┘    │              │    └──────────────┘ │
│                       │              │           │         │
│                       │              │           │ Fallback│
│                       │              │           ▼         │
│                       │              │    ┌──────────────┐ │
│                       │              └───▶│   DeepSeek   │ │
│                       │                     │   (Cloud)   │ │
│                       │                     └──────────────┘ │
│                       └─────────────────────────────┘      │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

---

## ✨ Características

| Característica | Descripción |
|----------------|-------------|
| 🔄 **Compatibilidad OpenAI** | Tus apps funcionan sin cambios |
| 🧠 **Routing Inteligente** | Detecta complejidad y decide el modelo |
| 💰 **Fallback Automático** | Si el local falla, usa DeepSeek |
| 📊 **Logging Completo** | Control de uso y costos |
| 🚦 **Rate Limiting** | Control de requests por usuario |
| 🔒 **API Key Auth** | Seguridad con keys personalizables |
| 📈 **Escalable** | Docker, systemd, Nginx ready |
| 🎯 **Modelos Flexibles** | Soporta Ollama, DeepSeek, y más |

### Modelos Soportados

| Modelo | Tipo | Costo | Mejor Para |
|--------|------|-------|------------|
| Qwen 2.5 7B | Local | $0 | Chat general |
| Llama 3.2 3B | Local | $0 | Respuestas rápidas |
| Mistral 7B | Local | $0 | Balanceado |
| DeepSeek Chat | Cloud | $0.0001/M | Tasks complejos |
| DeepSeek Coder | Cloud | $0.0001/M | Código |

---

## 🏗️ Arquitectura

```
unified-ai-api/
├── api/
│   ├── routes/
│   │   ├── chat.py          # /v1/chat/completions
│   │   ├── models.py        # /v1/models
│   │   └── health.py        # /health
│   ├── services/
│   │   ├── local_model.py   # Ollama integration
│   │   ├── remote_model.py  # DeepSeek API
│   │   └── router.py        # Decision engine
│   └── middleware/
│       ├── auth.py          # API key validation
│       ├── rate_limit.py    # Rate limiting
│       └── logging.py       # Request logging
├── config/
│   ├── settings.py          # Configuración
│   └── prompts.py           # System prompts
├── tests/
│   └── test_api.py
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .env.example
└── run.py
```

### Flujo de una Solicitud

```
1. Cliente envía request
         │
         ▼
2. Validar API Key + Rate Limit
         │
         ▼
3. Extraer parámetros (model, messages, etc.)
         │
         ▼
4. Determinar complejidad de la solicitud
         │
         ▼
    ┌────┴────┐
    │         │
   Simple   Compleja
    │         │
    ▼         ▼
Ollama   DeepSeek
    │         │
    └────┬────┘
         │
         ▼
5. Convertir respuesta al formato OpenAI
         │
         ▼
6. Retornar al cliente
```

---

## 💻 Requisitos

### Servidor de Producción

| Componente | Mínimo | Recomendado |
|------------|--------|-------------|
| CPU | 8 núcleos | 12+ núcleos |
| RAM | 16 GB | 24 GB |
| Storage | 100 GB SSD | 500 GB SSD |
| Red | 100 Mbps | 1 Gbps |

### Software Requerido

- Python 3.11+
- Ollama (para modelos locales)
- Redis (opcional, para rate limiting)
- Docker & Docker Compose (opcional)

---

## 🚀 Instalación

### Opción 1: Docker Compose (Recomendado)

```bash
# Clonar el repositorio
git clone https://github.com/tecnotactil-ia/unified-ai-api.git
cd unified-ai-api

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus configuraciones

# Iniciar servicios
docker-compose up -d
```

### Opción 2: Instalación Manual

```bash
# Clonar repositorio
git clone https://github.com/tecnotactil-ia/unified-ai-api.git
cd unified-ai-api

# Crear entorno virtual
python3 -m venv venv
source venv/bin/activate

# Instalar dependencias
pip install -r requirements.txt

# Instalar Ollama (en otro servidor o local)
curl -fsSL https://ollama.ai/install.sh | sh

# Descargar modelos
ollama pull qwen2.5:7b
ollama pull llama3.2:3b

# Configurar
cp .env.example .env
# Editar .env con tus API keys

# Iniciar
python run.py
```

### Configuración

```bash
# .env
HOST=0.0.0.0
PORT=8080

# Ollama
OLLAMA_URL=http://localhost:11434

# DeepSeek
DEEPSEEK_API_KEY=sk-tu-api-key

# API Keys (separadas por coma)
API_KEYS=sk-test-123,sk-prod-456
```

---

## 📖 Uso

### Ejemplo con cURL

```bash
# Request simple (usa modelo local)
curl -X POST http://localhost:8080/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer sk-tu-api-key" \
  -d '{
    "model": "qwen2.5:7b",
    "messages": [
      {"role": "user", "content": "Hola, ¿cómo estás?"}
    ],
    "temperature": 0.7
  }'
```

### Con Python (compatible con OpenAI SDK)

```python
from openai import OpenAI

# Configurar cliente
client = OpenAI(
    base_url="http://tu-servidor:8080/v1",
    api_key="sk-tu-api-key"
)

# Usar exactamente igual que OpenAI
response = client.chat.completions.create(
    model="qwen2.5:7b",
    messages=[
        {"role": "system", "content": "Eres un asistente útil."},
        {"role": "user", "content": "Explica qué es Python"}
    ],
    temperature=0.7
)

print(response.choices[0].message.content)
```

### Health Check

```bash
curl http://tu-servidor:8080/health
```

```json
{
  "status": "healthy",
  "ollama": "connected",
  "deepseek": "connected",
  "models": ["qwen2.5:7b", "llama3.2:3b"]
}
```

---

## 💰 Ahorro de Costos

### Escenario Real

| Métrica | Solo Cloud | Con Unified AI API |
|---------|------------|-------------------|
| Requests/mes | 10,000 | 10,000 |
| Costo/request | $0.02 | $0.005 |
| **Costo Total/mes** | **$200** | **$50** |
| **Ahorro** | - | **75%** |

### Proyección Anual

```
Solo Cloud:      $2,400/año
Con Unified AI:  $600/año
────────────────────────────
Ahorro Total:    $1,800/año
```

### ROI

| Inversión | Retorno (1 año) |
|-----------|-----------------|
| $100 (VPS) | $1,800 ahorros |
| **ROI** | **1,700%** |

---

## 🧪 Tests

```bash
# Ejecutar tests
pytest tests/ -v

# Con cobertura
pytest --cov=api tests/
```

---

## 🤝 Contribución

Las contribuciones son bienvenidas. Por favor lee [CONTRIBUTING.md](CONTRIBUTING.md) para detalles.

1. Fork el repositorio
2. Crea tu branch (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add some AmazingFeature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abre un Pull Request

---

## 📄 Licencia

Este proyecto está bajo la Licencia MIT - ver el archivo [LICENSE](LICENSE) para detalles.

---

## 👨‍💻 Autor

<div align="center">

### Felix Rodríguez Roble
**Ingeniero y Desarrollador Principal**

[![GitHub](https://img.shields.io/badge/GitHub-tecnotactil--ia-black?style=for-the-badge&logo=github)](https://github.com/tecnotactil-ia)
[![Email](https://img.shields.io/badge/Email-felix.roble@tecnotactil.com-red?style=for-the-badge&logo=gmail)](mailto:felix.roble@tecnotactil.com)

**Desarrollado con la asistencia de IAFasioBoy (AI Assistant)**

---

*Proyecto creado el 31 de enero de 2026*

</div>

---

<div align="center">

### ⭐ Si te gusta este proyecto, dale una estrella en GitHub!

[![GitHub stars](https://img.shields.io/github/stars/tecnotactil-ia/unified-ai-api?style=social)](https://github.com/tecnotactil-ia/unified-ai-api/stargazers)

</div>
