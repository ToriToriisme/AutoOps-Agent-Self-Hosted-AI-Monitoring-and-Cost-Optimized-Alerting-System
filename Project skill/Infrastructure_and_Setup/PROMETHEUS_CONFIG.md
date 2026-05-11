# Cấu hình Prometheus

Sử dụng kiến trúc pull-based để thu thập dữ liệu time-series [4].

```yaml
# prometheus.yml
global:
  scrape_interval: 15s # Chu kỳ quét dữ liệu [13]

scrape_configs:
  - job_name: 'node_exporter'
    static_configs:
      - targets: ['localhost:9100']
  - job_name: 'cadvisor'
    static_configs:
      - targets: ['localhost:8080']
```
