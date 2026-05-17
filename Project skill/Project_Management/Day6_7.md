# Day 6 & 7 — Xây dựng AutoOps Agent (Bộ Não AI Tự Động Hóa)

## 1) Mục tiêu của Day 6 & 7
Trong Day 5, Grafana đang đóng vai trò là người gửi tin nhắn trực tiếp cho bạn. Ở Day 6 & 7, chúng ta sẽ chèn một con "Robot" tên là **AutoOps Agent** vào giữa. Con Robot này sẽ nhận lỗi từ Grafana, suy nghĩ phân tích (bằng AI), tự động sửa những lỗi cơ bản (ổ cứng đầy, ứng dụng treo), và cuối cùng mới báo cáo lại cho bạn.

**Mục tiêu MVP:**
- Viết một Webhook Server bằng Python (dùng FastAPI hoặc Flask) để hứng cảnh báo từ Grafana.
- Tích hợp AI (LLM như Gemini hoặc OpenAI) để phân tích nguyên nhân lỗi.
- Viết kịch bản tự động sửa lỗi (Automated Remediation) bằng PowerShell cho cảnh báo "Ổ cứng sắp đầy".
- Gửi báo cáo cuối cùng (Gồm: Phân tích của AI + Kết quả tự sửa lỗi) về Telegram/Discord của bạn.

---

## 2) Kiến trúc của AutoOps Agent

Agent hoạt động theo quy trình 4 bước khép kín (OODA Loop):
1. **Observe (Quan sát):** Cổng Webhook `/api/v1/alerts/webhook` nhận gói tin JSON từ Grafana.
2. **Orient (Phân tích):** Trích xuất thông tin lỗi và gửi cho LLM (AI) để phân tích xem chuyện gì đang xảy ra.
3. **Decide (Ra quyết định):** Dựa vào tên lỗi (AlertName), quyết định xem có nên tự sửa không. 
   - Lỗi *Critical*: Báo cáo khẩn cấp, chờ người duyệt.
   - Lỗi *Warning*: Kích hoạt hàm tự động sửa lỗi.
4. **Act (Hành động):** Chạy PowerShell script (ví dụ xoá file rác) và gửi tin nhắn kết quả lên nhóm chat Telegram/Discord.

---

## 3) Việc cần làm (Checklist)

### 3.1 Cấu hình và phát triển Webhook Server trên thư mục `agent_api`
- Sử dụng thư mục `agent_api` có sẵn trong dự án (đây chính là nơi triển khai mã nguồn của AutoOps Agent).
- Tạo môi trường ảo (virtualenv) và cài đặt các thư viện cần thiết từ `requirements.txt`:
  ```powershell
  python -m venv .venv
  .\.venv\Scripts\pip install -r requirements.txt
  ```
- Phát triển tiếp logic trong file `app/main.py` đã dựng sẵn server FastAPI với endpoint `POST /api/v1/alerts/webhook` để hứng và xử lý dữ liệu nhận được.

### 3.2 Đổi hướng Grafana Webhook
- Quay lại Grafana -> Alerting -> Contact Points.
- Sửa lại cái Contact Point hiện tại (hoặc tạo mới) sang loại **Webhook**.
- Ở ô Webhook URL, hãy trỏ về server Python của bạn (Ví dụ: `http://host.docker.internal:8000/api/v1/alerts/webhook` hoặc dùng ngrok).
- Bấm Test bên Grafana để đảm bảo màn hình terminal của Python nhảy ra đống dữ liệu JSON.

### 3.3 Tích hợp LLM (Gemini/OpenAI)
- Lấy API Key từ Google AI Studio (cho Gemini) hoặc OpenAI.
- Trích xuất tên cảnh báo, trạng thái, và mô tả từ file JSON của Grafana.
- Viết một câu Prompt xịn xò: *"Hệ thống tôi vừa có cảnh báo [Tên lỗi], trạng thái [Firing]. Hãy đóng vai một DevOps Senior, giải thích ngắn gọn nguyên nhân có thể xảy ra và đề xuất hướng giải quyết."*
- Nhận và lưu lại câu trả lời phân tích của AI.

### 3.4 Lập trình module Tự Động Sửa Lỗi (Auto-Remediation)
- Cấu hình một bộ "Router" đơn giản trong Python: Nếu nhận được cảnh báo tên là `"Windows C: Drive Low Space"` thì kích hoạt hàm `remediate_low_disk()`.
- Hàm `remediate_low_disk()` sẽ sử dụng thư viện `subprocess` của Python để chạy ngầm lệnh PowerShell giúp dọn dẹp thư mục Temp: 
  `Remove-Item -Path "C:\Windows\Temp\*" -Recurse -Force -ErrorAction SilentlyContinue`

### 3.5 Bắn báo cáo về Telegram/Discord
- Viết hàm `send_telegram(message)` hoặc `send_discord(message)`.
- Ghép nối tất cả lại thành một luồng duy nhất: **Nhận Alert -> AI Phân tích -> Chạy Script Fix lỗi -> Soạn tin nhắn tổng hợp -> Gửi lên Telegram.**

---

## 4) Kiểm tra và Nghiệm thu (Definition of Done - DoD)
- [ ] Server Python (FastAPI) chạy thành công và nhận được dữ liệu Payload từ Grafana.
- [ ] AI phân tích thành công và trả về lời giải thích tiếng Việt chuyên nghiệp cho lỗi đó.
- [ ] Agent gọi thành công lệnh PowerShell dọn dẹp rác khi test lỗi Ổ Cứng Đầy.
- [ ] Điện thoại nhận được tin nhắn trên Telegram/Discord từ Agent (không phải từ Grafana) với nội dung chi tiết do AI soạn thảo và báo cáo kết quả dọn rác.

---

## 5) Timebox gợi ý (Tổng cộng khoảng 2 - 2.5 tiếng)
- **40 phút:** Cài đặt FastAPI, trỏ Grafana Webhook về Python và đọc được cục JSON.
- **30 phút:** Ghép nối API của Gemini/OpenAI vào luồng code.
- **30 phút:** Code phần thực thi câu lệnh PowerShell tự sửa lỗi.
- **30 phút:** Gắn API của Telegram/Discord Bot vào, test toàn bộ luồng từ A-Z bằng cách ép lỗi trên Grafana (đổi điều kiện <10 thành <99 giống Day 5).

## Bước tiếp theo (Sau Day 7)
Chạy mượt toàn bộ luồng này nghĩa là hệ thống AI AutoOps MVP của bạn đã hoàn thành tới 90% (Thậm chí đủ sức mang đi bảo vệ đồ án). Những ngày còn lại (Day 8+) chúng ta sẽ chỉ tập trung vào việc đóng gói code (Dockerize), làm sạch code, xử lý bảo mật và hoàn thiện báo cáo thuyết trình!
