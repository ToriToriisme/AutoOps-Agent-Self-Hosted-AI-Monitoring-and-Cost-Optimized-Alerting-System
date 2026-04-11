# Tài liệu API Nội bộ (Internal APIs)

Định nghĩa giao tiếp giữa Alertmanager và AI Agent Webhook:
- `POST /api/v1/alerts/webhook`
  - Nhận JSON Array từ Prometheus.
- `POST /api/v1/agent/approve/{task_id}`
  - Nút bấm trên Grafana sẽ gọi API này để mở khóa cho AI chạy tác vụ Medium.
