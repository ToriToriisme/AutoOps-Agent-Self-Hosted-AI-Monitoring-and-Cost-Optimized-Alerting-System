# Day 10 — Xử lý luồng MEDIUM (Pending Approval) & CRITICAL (Telegram Alert)

## 1) Mục tiêu của Day 10
Đây là ngày chúng ta hoàn thiện kiến trúc cốt lõi của AutoOps Agent, biến nó thành một hệ thống thực tế có khả năng đánh giá rủi ro và thông báo:
- **Luồng CRITICAL (Báo động khẩn cấp):** Khi hệ thống sập (Host Down) hoặc gặp sự cố cực kỳ nghiêm trọng, Agent không tự ý sửa mà lập tức gửi tin nhắn trực tiếp qua Telegram tới Admin.
- **Luồng MEDIUM (Chờ phê duyệt - Pending):** Khi mức độ ở mức vừa (CPU cao, RAM đầy), Agent sẽ tạo một Task lưu vào Database ở trạng thái `pending`, chờ Admin vào xem và duyệt mới được chạy lệnh sửa chữa.

---

## 2) Các bước thực hiện

### 2.1 Tích hợp Telegram Alert cho luồng CRITICAL
Thêm cấu hình `TELEGRAM_BOT_TOKEN` và `TELEGRAM_CHAT_ID` vào file `.env`. Trong `main.py`, hàm `send_telegram_alert` sử dụng API của Telegram để gửi tin nhắn Markdown trực quan, bao gồm:
- Tên sự cố & Trạng thái.
- **Phân tích nguyên nhân và cách xử lý từ Gemini AI (DevOps Senior)**.

```python
def send_telegram_alert(payload: GrafanaWebhookPayload, ai_analysis: str = "") -> bool:
    # ...
    text = (
        f"🚨 **HỆ THỐNG PHÁT HIỆN SỰ CỐ** 🚨\n\n"
        f"🔹 **Cảnh báo:** {payload.title}\n"
        f"🔹 **Trạng thái:** {payload.status.upper()}\n\n"
        f"🧠 **PHÂN TÍCH TỪ AI (DevOps Senior):**\n"
        f"{ai_analysis if ai_analysis else 'AI đang bận, vui lòng kiểm tra log.'}"
    )
    # ...
```

### 2.2 Quản lý vòng đời sự cố trong Database (Audit & Pending)
Trong hàm `process_alert_workflow`, hệ thống sử dụng các hàm từ `database.py` để tạo bản ghi `agent_tasks`. Tùy theo `severity` mà hành xử khác nhau:

- **SMALL:** Gọi `run_script` ngay lập tức -> Đổi status thành `executed`.
- **MEDIUM:** Không làm gì thêm -> Đổi status thành `pending` (treo lại chờ duyệt).
- **CRITICAL:** Gọi `send_telegram_alert` -> Đổi status thành `notified`.

Sau đó, tất cả kết quả đều được ghi vào bảng `audit_logs` để truy vết SLA (Processing Time) và kết quả chạy.

### 2.3 Chạy ngầm (Background Tasks)
Việc gọi Gemini AI và gửi Telegram có thể mất vài giây. Để tránh làm timeout Grafana Webhook, toàn bộ `process_alert_workflow` được đẩy vào `BackgroundTasks` của FastAPI. Agent sẽ phản hồi mã `200 OK` cho Grafana ngay lập tức.

---

## 3) Kiểm tra và Nghiệm thu (Definition of Done - DoD)
- [ ] **CRITICAL:** Gửi giả lập alert chứa chữ "Down", điện thoại nhận được tin nhắn Telegram cực kỳ chi tiết có kèm nhận định của AI.
- [ ] **MEDIUM:** Gửi giả lập alert "CPU High", mở file SQLite Database (`storage/autoops_agent.db`) thấy có bản ghi trong bảng `agent_tasks` lưu trạng thái `pending`.
- [ ] **SLA Response:** Grafana không bị báo lỗi Timeout do Webhook mất quá nhiều thời gian phản hồi (nhờ BackgroundTasks).

---
**Chúc mừng!** Bạn đã hoàn thiện MVP (Minimum Viable Product) cho một AI Agent thực thụ dành cho DevOps, có đủ luồng suy luận, an toàn (Circuit Breaker/Whitelist) và giao tiếp (Telegram/Audit). Các ngày tiếp theo sẽ tập trung tinh chỉnh và làm giao diện (nếu cần).
