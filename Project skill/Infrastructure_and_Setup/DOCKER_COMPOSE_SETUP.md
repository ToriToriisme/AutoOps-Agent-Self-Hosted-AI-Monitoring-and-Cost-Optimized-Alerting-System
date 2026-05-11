# Cấu hình Docker Compose Tổng thể

```yaml
version: '3.8'
services:
  prometheus:
    image: prom/prometheus
    volumes: ['./prometheus.yml:/etc/prometheus/prometheus.yml']
  grafana:
    image: grafana/grafana
    ports: ['3000:3000']
  cadvisor:
    image: google/cadvisor
  ai_agent_backend:
    build: ./agent_api
    environment:
      - OLLAMA_HOST=http://host.docker.internal:11434
```
