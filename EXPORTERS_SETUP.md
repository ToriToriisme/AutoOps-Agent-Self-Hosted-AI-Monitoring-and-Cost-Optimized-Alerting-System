# Cài đặt Exporters

Để Prometheus lấy được dữ liệu, cần cài đặt các exporter:
1. **Node Exporter:** Lấy thông số hệ điều hành (CPU, RAM, Disk, Network) [14].
2. **cAdvisor (Container Advisor):** Lấy dữ liệu per-container từ Docker daemon [15, 16].

Chạy bằng Docker:

```bash
docker run -d --name=cadvisor -p 8080:8080 -v /:/rootfs:ro -v /var/run:/var/run:ro -v /sys:/sys:ro -v /var/lib/docker/:/var/lib/docker:ro google/cadvisor:latest
```
