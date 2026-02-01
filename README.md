# Unified AI API Gateway

Unified AI API Gateway compatible con OpenAI API que combina modelos locales (Ollama) con DeepSeek como fallback.

## Musica del Autor

**Sígueme en:**
- YouTube: https://www.youtube.com/channel/UC9IAc-g90R7OFWOWP47M4LQ
- Spotify: https://open.spotify.com/intl-es/artist/7vuYQjvp1NlUzkBd1v4I4k?si=25c6645728354523

---

## Instalacion Manual (Tutorial Paso a Paso)

### Requisitos
- Ubuntu 24.04
- Al menos 8GB RAM
- Dominio configurado (bak.tudominio.com)
- API Key de DeepSeek (opcional)

### Paso 1: Conectar al VPS

```bash
ssh root@tu-ip-del-vps
```

### Paso 2: Instalar Dependencias

```bash
apt-get update -qq
apt-get upgrade -y
apt-get install -y curl wget git vim python3 python3-pip python3-venv nginx
```

### Paso 3: Instalar Ollama

```bash
curl -fsSL https://ollama.ai/install.sh | sh
systemctl enable ollama
systemctl start ollama
```

### Paso 4: Descargar Modelo Local

```bash
ollama pull qwen2.5:7b
```

### Paso 5: Clonar Repositorio

```bash
cd /root
git clone https://github.com/tecnotactil-ia/unified-ai-api.git
cd unified-ai-api
chmod +x install-ai-gateway.sh
```

### Paso 6: Ejecutar Instalador

```bash
./install-ai-gateway.sh
```

### Paso 7: Configurar Variables de Entorno

```bash
cp .env.example .env
nano .env
# Editar con tus API keys
```

### Paso 8: Crear y configurar servicios systemd

Ver archivo install-ai-gateway.sh para detalles de los servicios.

### Paso 9: Configurar Nginx y SSL

```bash
cat > /etc/nginx/sites-available/ai-gateway << 'EOF'
server {
    server_name tu-dominio.com;

    location /v1/ {
        proxy_pass http://127.0.0.1:8080;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    location /api/manager {
        proxy_pass http://127.0.0.1:8081;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
    }

    listen 443 ssl;
    ssl_certificate /etc/letsencrypt/live/tu-dominio.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/tu-dominio.com/privkey.pem;
}
EOF

ln -sf /etc/nginx/sites-available/ai-gateway /etc/nginx/sites-enabled/
nginx -t
systemctl reload nginx

# Obtener SSL
certbot --nginx -d tu-dominio.com --non-interactive --agree-tos -m tu@email.com
```

---

## Endpoints

| Metodo | Endpoint | Descripcion |
|--------|----------|-------------|
| POST | /v1/chat/completions | Chat API (OpenAI compatible) |
| GET | /v1/models | Listar modelos |
| GET | /health | Health check |
| POST | /api/manager | Gestion remota |

---

## Uso de la API

### Chat con modelo local

```bash
curl -X POST https://tu-dominio/v1/chat/completions \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TU_API_KEY" \
  -d '{
    "model": "qwen2.5:7b",
    "messages": [{"role": "user", "content": "Hola"}]
  }'
```

### Gestion remota

```bash
# Crear API key
curl -X POST https://tu-dominio/api/manager \
  -H "Content-Type: application/json" \
  -H "X-Manager-API-Key: TU_MANAGER_KEY" \
  -d '{"command":"crea una API key para MiApp"}'
```

---

## Arquitectura

```
                    tu-dominio.com
                         |
           +-------------+-------------+
           |                           |
    +------v------+           +-------v------+
    |   Ollama    |           |   DeepSeek   |
    | Qwen 2.5 7B |           |   Fallback   |
    |   (Local)   |           |              |
    +-------------+           +--------------+
```

---

## Caracteristicas

- Compatible con OpenAI API
- Modelos locales gratuitos (Ollama)
- Fallback a DeepSeek (mas economico que GPT-4)
- Gestion de API keys
- Registro de uso
- Acceso via Nginx + SSL

---

## Licencia

MIT

---

## Autor

**TecnoTactil**

- YouTube: https://www.youtube.com/channel/UC9IAc-g90R7OFWOWP47M4LQ
- Spotify: https://open.spotify.com/intl-es/artist/7vuYQjvp1NlUzkBd1v4I4k

---

## Agente IA

Desarrollado con ayuda de IAFasioBot - Asistente IA de codigo abierto.
