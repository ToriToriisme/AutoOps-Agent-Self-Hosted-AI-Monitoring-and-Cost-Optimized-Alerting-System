# Thiết kế Hệ thống Cấp thấp (Low-Level Design)

LLD trình bày chi tiết logic thực thi, thuật toán và cấu trúc dữ liệu của các mô-đun trong HLD [12].

## 1. Database Schema (PostgreSQL/SQLite)

- `alerts_table` (id, node_name, severity, status).
- `ai_logs_table` (run_id, intermediate_steps, prompt_tokens, tools_used).

## 2. Logic Phân loại (Triage Logic)

- Hàm `evaluate_severity(alert_json, rag_context)` trả về enum `[SMALL, MEDIUM, CRITICAL]`.
- Mạch ngắt (Circuit Breaker): Tự động block nếu AI gọi Tool không tồn tại.
