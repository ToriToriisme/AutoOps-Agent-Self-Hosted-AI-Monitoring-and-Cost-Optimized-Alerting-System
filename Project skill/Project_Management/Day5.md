# Day 5 — Cấu hình Grafana Alerting (Hệ thống Cảnh báo Tự động)

## 1) Mục tiêu của Day 5

Ở Day 4, bạn đã có một Dashboard giám sát cực kỳ xịn xò. Tuy nhiên, hệ thống giám sát đúng nghĩa không phải là bắt con người phải ngồi nhìn chằm chằm vào màn hình 24/7.
Mục tiêu cốt lõi của hôm nay là biến hệ thống giám sát thành **Chủ động (Proactive)**: Tự động phát hiện khi máy chủ gặp vấn đề (ví dụ: CPU quá tải, ổ cứng sắp đầy, máy chủ mất kết nối) và "bắn" thông báo ra bên ngoài.

**Mục tiêu MVP cho hôm nay:**
- Làm quen với hệ thống Alerting thế hệ mới của Grafana.
- Thiết lập thành công 3 luật cảnh báo cơ bản nhất cho Windows.
- Cấu hình một kênh nhận thông báo (Contact Point) để test (có thể dùng webhook.site hoặc Discord/Telegram). Bước này là tiền đề cực kỳ quan trọng để sau này bắn cảnh báo về cho **AutoOps Agent (AI)** tự động xử lý.

---

## 2) Những khái niệm cần nắm rõ

### 2.1 Thành phần của Grafana Alerting
Grafana Alerting bao gồm 3 thành phần chính liên kết với nhau:
1. **Alert Rules (Luật cảnh báo):** Nơi bạn định nghĩa "Thế nào là lỗi?". Ví dụ: `CPU > 80% trong vòng 5 phút`.
2. **Contact Points (Điểm tiếp nhận):** Nơi bạn muốn Grafana gửi tin nhắn tới khi có lỗi (ví dụ: Slack, Discord, Email, Webhook).
3. **Notification Policies (Chính sách thông báo):** Người đứng giữa làm nhiệm vụ phân luồng. Ví dụ: Nếu là lỗi "Nghiêm trọng (Critical)" thì gửi vào kênh Discord A, nếu là cảnh báo "Nhắc nhở (Warning)" thì gửi vào kênh B.

### 2.2 Trạng thái của một Alert
- **Normal (Xanh):** Bình thường, mọi thứ ổn định.
- **Pending (Vàng):** Điều kiện lỗi đã xảy ra, nhưng Grafana đang "chờ thêm một chút" xem nó có tự hết không (để tránh báo động giả - false alarm do máy tính chỉ bị lag vài giây).
- **Firing (Đỏ):** Đã hết thời gian chờ mà lỗi vẫn còn. Còi báo động chính thức kêu, tin nhắn được bắn đi!

---

## 3) Việc cần làm trong Day 5 (Checklist)

### 3.1 Cấu hình Contact Point (Nơi nhận cảnh báo)
- Truy cập Grafana, chọn menu **Alerting** -> **Contact points**.
- Thêm một Contact point mới. 
- *Gợi ý:* Để test nhanh nhất, bạn có thể tạo một kênh Discord, vào phần Integration tạo một Webhook URL, sau đó dán vào Grafana (chọn loại là Discord). Hoặc dùng trang web `https://webhook.site/` để hứng dữ liệu.
- Bấm **Test** để đảm bảo Grafana có thể gửi tin nhắn ra ngoài thành công.

### 3.2 Thiết lập Notification Policy
- Vào menu **Alerting** -> **Notification policies**.
- Sửa cái `Default policy` (Chính sách mặc định) để nó trỏ tới cái Contact Point bạn vừa tạo ở bước 3.1. (Nghĩa là mọi cảnh báo sinh ra mặc định sẽ gửi hết về Discord/Webhook của bạn).

### 3.3 Tạo Alert Rules (Luật cảnh báo)
Vào **Alerting** -> **Alert rules** và tạo 3 luật sau:

**Luật 1: Máy chủ mất kết nối (Instance Down) - CRITICAL**
- Sử dụng query: `up{job="windows_exporter"} == 0`
- Thời gian chờ (Pending period): `1m` (1 phút).

**Luật 2: CPU quá tải (High CPU Usage) - WARNING**
- Bạn có thể lấy lại câu query CPU từ Dashboard Day 4.
- Đặt điều kiện: Nếu CPU > `80%`.
- Thời gian chờ: `3m` (để tránh việc mở app nặng làm CPU vọt lên rồi lại xuống).

**Luật 3: Ổ cứng sắp đầy (Low Disk Space) - WARNING**
- Đặt điều kiện: Dung lượng trống (Free space) của ổ C: < `10%`.
- Thời gian chờ: `5m`.

### 3.4 Test thử hệ thống (Simulate Alert)
- Để test xem cảnh báo có hoạt động không, bạn có thể hạ mức chịu đựng xuống. Ví dụ: Sửa luật CPU thành `> 10%`.
- Mở một vài phần mềm nặng trên máy Windows để CPU vọt lên trên 10%.
- Quan sát trạng thái Alert chuyển từ `Normal` -> `Pending` -> `Firing`.
- Mở Discord / Webhook ra check xem có tin nhắn báo động gửi về không!

---

## 4) Kiểm tra và Nghiệm thu (Definition of Done - DoD)

- [ ] Đã tạo thành công ít nhất 3 Alert Rules cơ bản.
- [ ] Contact Point đã được test thành công (kết nối được ra bên ngoài).
- [ ] Đã ép cho một Alert chuyển sang trạng thái `Firing` thành công.
- [ ] Nhận được tin nhắn/dữ liệu cảnh báo gửi về hệ thống (Discord/Webhook).

---

## 5) Timebox gợi ý trong Day 5

- **15 phút**: Tìm hiểu về khái niệm Alert Rule và Contact Point.
- **15 phút**: Cấu hình Contact Point (Discord/Webhook) và Notification Policy.
- **20 phút**: Viết và cấu hình 3 Alert Rules.
- **10 phút**: Test thử hệ thống bằng cách ép cho CPU tăng cao hoặc chỉnh lại điều kiện báo động.

## Bước tiếp theo (Preview Day 6)
Khi Grafana đã biết cách "kêu la" khi có lỗi, Day 6 sẽ là một bước ngoặt: Chúng ta sẽ xây dựng **Webhook Server (AutoOps Agent backend)** để "hứng" các cảnh báo này từ Grafana, sau đó chuyển giao cho AI (LLM) phân tích và đưa ra giải pháp tự động!
