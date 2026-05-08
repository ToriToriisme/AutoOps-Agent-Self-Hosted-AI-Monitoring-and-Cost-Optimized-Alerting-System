# Quy tắc Cảnh báo (Alerting Rules)

Định nghĩa khi nào Prometheus sẽ bắn Webhook cho AI Agent [19].

```yaml
# alerts.yml
groups:
- name: AI_Agent_Alerts
  rules:
  - alert: HighCPULoad
    expr: 100 - (avg by (instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 90
    for: 2m
    labels:
      severity: warning
    annotations:
      summary: "CPU vượt 90% trên {{ $labels.instance }}"
```
