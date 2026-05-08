# Lịch 14 ngày hoàn thiện đồ án (Monitoring cho Windows + AutoOps/AI)

## Mục tiêu MVP (kết thúc ngày 14)

- **Monitoring Windows**: thu thập CPU, RAM, Disk, Network, trạng thái service/process cơ bản và (tuỳ chọn) Windows Event Logs.
- **Observability stack**: Prometheus + Grafana chạy bằng Docker Compose.
- **Alerting**: Grafana Unified Alerting bắn webhook về Backend (FastAPI).
- **AutoOps/AI (MVP)**: Backend triage cảnh báo (SMALL/MEDIUM/CRITICAL) + ghi audit + (tuỳ chọn) gọi LLM nội bộ (Ollama) theo policy.
- **Deliverable**: demo end-to-end + tài liệu cài đặt + hướng dẫn sử dụng + kịch bản demo.

---

## Ngày 1 — Chốt phạm vi + kiến trúc + tiêu chí chấm

- **Tools cần dùng**
  - Git/GitHub, VS Code/Cursor, PowerShell
  - Mermaid (trong Markdown) hoặc diagrams.net
  - Các file trong thư mục `Project skill/` (SRS/HLD/LLD nếu có)
- **Các bước thực hiện**
  - Chốt MVP: chỉ chọn 5–8 metric quan trọng + 2–3 rule alert + 1 luồng AutoOps (SMALL/MEDIUM/CRITICAL).
  - Vẽ sơ đồ luồng: Prometheus → Grafana Alerting → Webhook → FastAPI → (Tool/Notify/Audit).
  - Viết “Definition of Done” (DoD) cho demo cuối.
- **Mục tiêu trong ngày**: khoá scope để 14 ngày làm kịp và demo được.
- **Kết quả kỳ vọng**: 1 trang mô tả MVP + 1 sơ đồ kiến trúc + danh sách rule/alert sẽ làm.

---

## Ngày 2 — Dựng stack quan sát (Docker Compose)

- **Tools cần dùng**
  - Docker Desktop, `docker compose`
  - Grafana, Prometheus
- **Các bước thực hiện**
  - Dựng `docker-compose.yml` theo hướng dẫn `Project skill/DOCKER_COMPOSE_SETUP.md`.
  - Bật Grafana + Prometheus chạy ổn định, volume persist.
  - Tạo cấu trúc thư mục cấu hình: `prometheus.yml`, provisioning dashboard/datasource (nếu dùng).
- **Mục tiêu trong ngày**: chạy được observability stack bằng 1 lệnh.
- **Kết quả kỳ vọng**: `docker compose up -d` chạy Grafana/Prometheus; truy cập được UI Grafana.

---

## Ngày 3 — Thu thập metric Windows (Windows Exporter hoặc agent)

- **Tools cần dùng**
  - **Khuyến nghị**: `windows_exporter` (Prometheus exporter cho Windows)
  - PowerShell, Windows Services, Firewall rules (nếu cần)
- **Các bước thực hiện**
  - Cài `windows_exporter` trên máy Windows mục tiêu (hoặc VM).
  - Mở endpoint metrics (thường `:9182/metrics`) và kiểm tra Prometheus scrape được.
  - Chọn collectors tối thiểu: cpu, memory, logical_disk, net, os, service/process (tuỳ).
- **Mục tiêu trong ngày**: có nguồn metric Windows chuẩn Prometheus.
- **Kết quả kỳ vọng**: Prometheus target “UP”; thấy metric Windows trong Prometheus/Grafana Explore.

---

## Ngày 4 — Dashboard Grafana cho Windows (MVP)

- **Tools cần dùng**
  - Grafana (dashboard + variables), Prometheus datasource
  - `Project skill/GRAFANA_DASHBOARD_SETUP.md`
- **Các bước thực hiện**
  - Tạo dashboard: CPU %, RAM used, Disk used %, Network RX/TX, host up/down.
  - Thêm biến `instance`/`job` để chọn host.
  - Export dashboard JSON để nộp kèm.
- **Mục tiêu trong ngày**: nhìn thấy “sức khoẻ Windows” realtime.
- **Kết quả kỳ vọng**: 1 dashboard chạy ổn; có file export dashboard.

---

## Ngày 5 — Alert rules trên Grafana (CPU/Disk/Host down)

- **Tools cần dùng**
  - Grafana Unified Alerting
  - PromQL
  - Tài liệu `Project skill/ALERTING_RULES.md`
- **Các bước thực hiện**
  - Tạo 3 alert rule:
    - **Host down**: `up == 0`
    - **Disk high**: disk used > 85–90% trong 5 phút
    - **CPU high**: CPU > 90% trong 5 phút
  - Tạo Contact Point dạng **Webhook** trỏ tới backend (sẽ làm ngày 6).
- **Mục tiêu trong ngày**: có cảnh báo hoạt động và test được.
- **Kết quả kỳ vọng**: rule evaluate OK; sẵn sàng bắn webhook khi vi phạm.

---

## Ngày 6 — Backend FastAPI nhận webhook alert (chuẩn hoá + lưu audit)

- **Tools cần dùng**
  - Python, FastAPI, Uvicorn
  - OpenAPI/Swagger (mặc định của FastAPI)
- **Các bước thực hiện**
  - Tạo endpoint nhận webhook (ví dụ: `POST /api/v1/alerts/webhook`).
  - Chuẩn hoá payload (tách title, severity, labels, annotations, timestamps).
  - Ghi audit tối thiểu (JSONL/SQLite) để truy vết: input → decision → action.
- **Mục tiêu trong ngày**: nhận alert từ Grafana và lưu được lịch sử.
- **Kết quả kỳ vọng**: Grafana test webhook trả 200; backend lưu bản ghi audit.

---

## Ngày 7 — Phân loại SMALL / MEDIUM / CRITICAL (rule-based trước)

- **Tools cần dùng**
  - FastAPI, Pydantic
  - Tài liệu `Project skill/SECURITY_AND_PRIVACY.md` (policy/least privilege)
- **Các bước thực hiện**
  - Viết “triage policy” đơn giản:
    - CRITICAL: host down, disk > 95%, nhiều alert đồng thời
    - MEDIUM: CPU/RAM spike ngắn, disk 85–95%
    - SMALL: cảnh báo mức thấp hoặc tự khắc phục (ví dụ restart service không quan trọng)
  - Lưu kết quả triage vào audit.
- **Mục tiêu trong ngày**: có logic phân loại mà không cần AI vẫn chạy được.
- **Kết quả kỳ vọng**: mỗi alert vào backend được gắn mức độ + lý do.

---

## Ngày 8 — Thực thi hành động “an toàn” (tool whitelist) cho SMALL

- **Tools cần dùng**
  - PowerShell scripts (đã whitelist), Windows permissions (least privilege)
  - `Project skill/TOOL_CALLING_FUNCTIONS.md` (định hướng tool calling)
- **Các bước thực hiện**
  - Tạo 1–2 script minh hoạ (ví dụ: dọn file tạm, restart service cụ thể).
  - Backend chỉ gọi script trong whitelist + validate tham số + timeout.
  - Ghi stdout/stderr tóm tắt vào audit.
- **Mục tiêu trong ngày**: “closed-loop” mức SMALL chạy được.
- **Kết quả kỳ vọng**: alert SMALL → backend chạy script → audit có kết quả.

---

## Ngày 9 — Luồng MEDIUM: pending approval (MVP không cần UI đẹp)

- **Tools cần dùng**
  - SQLite (hoặc file JSON) để lưu pending
  - Cách duyệt đơn giản: endpoint approve/reject (hoặc trang HTML minimal)
- **Các bước thực hiện**
  - Khi MEDIUM: lưu “pending action” (alert + đề xuất hành động + tham số).
  - Tạo endpoint:
    - `GET /api/v1/pending` (liệt kê)
    - `POST /api/v1/pending/{id}/approve`
    - `POST /api/v1/pending/{id}/reject`
  - Khi approve: mới được chạy tool whitelist.
- **Mục tiêu trong ngày**: có cơ chế “hỏi ý kiến” trước khi tự làm.
- **Kết quả kỳ vọng**: MEDIUM không tự chạy; chỉ chạy sau approve; audit đầy đủ.

---

## Ngày 10 — Luồng CRITICAL: thông báo khẩn (Telegram/Email/Discord)

- **Tools cần dùng**
  - Telegram Bot (khuyến nghị) hoặc Email SMTP/Discord webhook
  - Retry policy (backoff) tối thiểu
- **Các bước thực hiện**
  - Tích hợp 1 kênh notify cho CRITICAL.
  - Format message: host, rule, severity, thời gian, link dashboard/Explore, runbook (nếu có).
  - Test tình huống host down/disk full giả lập.
- **Mục tiêu trong ngày**: CRITICAL phải “báo ngay” và có context.
- **Kết quả kỳ vọng**: nhận được thông báo; message có link và thông tin đủ hành động.

---

## Ngày 11 — Tích hợp AI (Ollama) cho triage/đề xuất (giới hạn nghiêm ngặt)

- **Tools cần dùng**
  - Ollama (self-hosted LLM), prompt template
  - Tài liệu `Project skill/PROMPT_ENGINEERING.md` và `Project skill/LLM_OBSERVABILITY.md`
- **Các bước thực hiện**
  - Chỉ dùng AI để:
    - giải thích alert bằng ngôn ngữ tự nhiên
    - đề xuất mức độ + hành động *trong whitelist*
  - Bắt buộc output định dạng (JSON) + validate, nếu fail thì fallback rule-based.
  - Log token/cost nội bộ (nếu có) theo `Project skill/TOKEN_AND_COST_TRACKING.md`.
- **Mục tiêu trong ngày**: có “AI Analyst” nhưng không phá an toàn hệ thống.
- **Kết quả kỳ vọng**: alert → AI trả về đề xuất hợp lệ; nếu không hợp lệ thì fallback.

---

## Ngày 12 — (Tuỳ chọn) Event Logs / Logs pipeline cho Windows

- **Tools cần dùng**
  - PowerShell `Get-WinEvent` hoặc agent nhẹ
  - (Tuỳ) Loki/Promtail hoặc lưu DB/file
- **Các bước thực hiện**
  - Thu thập một số event quan trọng (Service crashed, Disk, Update errors).
  - Gắn event gần thời điểm alert để tăng ngữ cảnh cho AI.
  - Hiển thị được event theo host/time.
- **Mục tiêu trong ngày**: có “why” (log/event) cạnh “what” (metric).
- **Kết quả kỳ vọng**: xem được event theo khoảng thời gian; AI có thêm context khi trả lời.

---

## Ngày 13 — Kiểm thử + drill lỗi + hardening bảo mật

- **Tools cần dùng**
  - pytest (hoặc framework test), Postman
  - Threat checklist theo `Project skill/SECURITY_AND_PRIVACY.md`
- **Các bước thực hiện**
  - Test end-to-end: alert → webhook → triage → (pending/notify/tool) → audit.
  - Drill: backend down, tool timeout, payload lạ, spam alert.
  - Chốt cấu hình secrets qua `.env` (không commit), tài liệu hoá cấu hình.
- **Mục tiêu trong ngày**: hệ thống chịu lỗi tốt, demo không “toang”.
- **Kết quả kỳ vọng**: bộ test cơ bản + checklist hardening + demo chạy ổn.

---

## Ngày 14 — Đóng gói demo + tài liệu nộp + kịch bản thuyết trình

- **Tools cần dùng**
  - README/User Manual (tham chiếu `Project skill/USER_MANUAL.md`)
  - OBS/record screen (tuỳ), slide (tuỳ)
- **Các bước thực hiện**
  - Viết hướng dẫn cài đặt (Docker compose + Windows exporter + backend).
  - Chuẩn bị demo script 5–8 phút:
    - mở dashboard → tạo tình huống CPU/disk → alert → webhook → triage → notify/pending → audit.
  - Tổng hợp deliverables: dashboard export, cấu hình, ảnh/screencast.
- **Mục tiêu trong ngày**: gói bài hoàn chỉnh, dễ chấm, dễ chạy lại.
- **Kết quả kỳ vọng**: repo có tài liệu đầy đủ + demo end-to-end thành công.

---

## Checklist kết quả tối thiểu để “qua MVP”

- **Monitoring**: Prometheus scrape Windows target “UP”.
- **Dashboard**: có dashboard Windows cơ bản trên Grafana.
- **Alerting**: có ít nhất 3 rule, test được.
- **Webhook**: Grafana → FastAPI nhận và log audit.
- **AutoOps**: có triage + SMALL tool whitelist + MEDIUM pending + CRITICAL notify (tối thiểu 1 kênh).
- **Docs**: có hướng dẫn cài đặt + chạy demo.

