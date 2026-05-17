# Day 12 — Tích hợp Windows Event Logs (Nâng cao Ngữ cảnh AI)

## 1) Mục tiêu của Day 12
Sau khi hệ thống đã có khả năng Triage dựa trên thông số từ Grafana, mục tiêu của Day 12 là trang bị thêm "bối cảnh" (Context) cho AI bằng cách thu thập các bản ghi lỗi từ **Windows Event Logs**. Khi AI có log hệ thống, nó sẽ phân tích Root Cause chính xác hơn thay vì phỏng đoán chung chung.

> **Ghi chú Kiến trúc mở rộng (Scale-up lên 30 máy):**
> Ở phiên bản MVP (1 máy), AI Agent và Target Server chạy trên cùng máy vật lý nên chúng ta dùng `subprocess` để lấy Windows Event Log. Tuy nhiên, trong tương lai khi scale lên 30 máy, hệ thống sẽ được nâng cấp bằng cách cài đặt Promtail/Loki (Log Aggregation) trên các máy con để Backend gọi API query log tập trung, thay vì chạy PowerShell cục bộ.

---

## 2) Các bước thực hiện

### 2.1 Viết Script lấy Log & Tối ưu hóa Context (Sanitize)
Dùng `subprocess` để truy vấn Windows Event Logs, nhưng phải làm sạch dữ liệu để tránh lỗi "Context Stuffing" (nhiễu thông tin làm AI mất tập trung) và tránh các ký tự đặc biệt làm vỡ cấu trúc chuỗi JSON.
- **Lệnh PowerShell mẫu (Lọc 5 sự kiện lỗi gần nhất trong 15 phút):** 
  ```powershell
  Get-WinEvent -FilterHashtable @{LogName='System'; Level=2,3; StartTime=(Get-Date).AddMinutes(-15)} -MaxEvents 5 | Select-Object TimeCreated, Message
  ```
- **Hành động (Sanitize):** Viết thêm một hàm Python để cắt gọt khoảng trắng thừa, xóa các ký tự ngoặc kép/xuống dòng không cần thiết, và **giới hạn độ dài** (ví dụ: chỉ lấy 500 ký tự đầu tiên của mỗi Message).

### 2.2 Xử lý Kịch bản "Empty State" và Timeout
Hệ thống tự động không bao giờ được phép "treo" chờ một lệnh lấy log.
- Cấu hình `timeout=5` cho hàm `subprocess.run()`. Nếu quá 5 giây lệnh PowerShell không trả về, bắt buộc tự ngắt (raise TimeoutExpired).
- Bọc logic lấy log vào khối `try...except`. Nếu lỗi mạng, quá hạn, hoặc hệ thống thật sự không có lỗi nào được ghi nhận, gán biến dữ liệu log thành chuỗi: *"Không tìm thấy log trong 15 phút qua"*.
- **Cập nhật Prompt:** Dặn dò thêm Gemini: *"Nếu phần [Context] ghi là 'Không tìm thấy log...', hãy phân tích nguyên nhân chỉ dựa trên thông số của Grafana và ghi chú rõ là không có dữ liệu Event Log."*

### 2.3 Phân tích kết quả bằng AI
- Nhúng đoạn log đã được làm sạch vào Prompt Template (qua biến `{description}` hoặc `{event_logs}`).
- Đợi xem AI sẽ tận dụng Event ID hoặc Tên process bị lỗi trong Log để phán đoán chính xác như thế nào (ví dụ: "Sập Service Spooler do lỗi file DLL dựa trên Event ID 7034").

---

## 3) Kiểm tra và Nghiệm thu (Definition of Done - DoD)
- [ ] **Happy Path:** Gửi cảnh báo sự cố, Backend fetch thành công log lỗi, AI phân tích sâu và nhắc đến thông điệp lỗi (Event ID) trong trường `root_cause_analysis`.
- [ ] **Sad Path (Ngoại lệ & Timeout):** Cố tình giả lập lỗi bằng cách gõ sai lệnh PowerShell hoặc không có lỗi nào trong Windows. Đảm bảo Backend không bị crash, Background Task không bị treo, và AI vẫn trả về JSON hợp lệ với nội dung "Không có log".
- [ ] **Token Tracking (NFR-C1):** Query bảng `audit_logs` để quan sát sự chênh lệch số lượng Token tiêu thụ trước và sau khi nhúng log. Đảm bảo số `prompt_tokens` tăng lên do có thêm log, nhưng vẫn nằm trong ngưỡng kiểm soát chi phí an toàn của Gemini API.
