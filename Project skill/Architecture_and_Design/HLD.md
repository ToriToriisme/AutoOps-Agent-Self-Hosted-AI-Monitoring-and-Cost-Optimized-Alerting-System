# Thiết kế Hệ thống Cấp cao (High-Level Design)

HLD cung cấp cái nhìn tổng quan về kiến trúc và cách các mô-đun giao tiếp [11].

## 1. Các Lớp Kiến trúc

- **Monitoring Layer:** Prometheus, Exporters.
- **Alerting Layer (MVP):** Grafana Unified Alerting (đánh giá rule + webhook).
- **AI & RAG Layer:** Self-hosted LLM, Vector DB.
- **Visualization Layer:** Grafana Dashboard.
- **Execution Layer:** Scripts / Docker Socket.

## 2. Lưu đồ dòng dữ liệu (Data Flow)

`Server bị lỗi` -> `Prometheus scrape metrics` -> `Grafana Alerting bắn webhook` -> `AI Agent đọc dữ liệu` -> `Truy xuất RAG` -> `Phân loại (Small/Medium/Critical)` -> `Thực thi` -> `Lưu Log học lại`.
