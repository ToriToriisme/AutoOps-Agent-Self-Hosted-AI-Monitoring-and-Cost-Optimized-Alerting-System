# Day 14 — Đóng gói Demo, Tài liệu nộp và Kịch bản Thuyết trình

## 1) Mục tiêu của Day 14
Đưa dự án về đích. Trọng tâm của ngày cuối cùng không phải là code thêm tính năng, mà là "bán" sản phẩm. Bạn cần hoàn thiện các tài liệu (README), cấu hình Docker chuẩn mực và chuẩn bị một kịch bản "ăn điểm" cho buổi thuyết trình với hội đồng.

## 2) Các bước thực hiện

### 2.1 Hoàn thiện Tài liệu (Documentation)
Tài liệu `README.md` là ấn tượng đầu tiên của hội đồng. Cần bổ sung:
- **Sử dụng Hình ảnh/Biểu đồ:** Chèn ảnh chụp màn hình Dashboard Grafana, giao diện tin nhắn Telegram, và đặc biệt là sơ đồ luồng dữ liệu (OODA Loop: Grafana -> FastAPI -> Gemini -> PowerShell).
- **Tạo file `.env.example`:** Tuyệt đối không commit file `.env` thật có chứa API Key lên GitHub để tránh rò rỉ bảo mật. Thay vào đó, hãy tạo file mẫu (ví dụ: `GOOGLE_API_KEY=your_key_here`) để người khác clone về biết cách cấu hình.
- **Làm rõ các tiêu chuẩn NFRs:** Tóm tắt nhanh thành quả dự án:
  - Hệ thống tự giải quyết sự cố, đáp ứng **SLA < 30s** (NFR-P1).
  - Bảo mật bằng Circuit Breaker đảm bảo **Least Privilege** (NFR-S2).
  - Tối ưu hóa chi phí API bằng LLM Observability (NFR-C1).

### 2.2 Đóng gói Hệ thống (Deployment)
- **Docker Volumes cho SQLite:** Khi đóng gói Agent API bằng Docker, hãy chắc chắn rằng bạn đã map volume cho thư mục chứa database (`storage/`). Nếu không, mỗi khi restart bằng lệnh `docker-compose down/up`, lịch sử `audit_logs` sẽ bị xóa sạch, khiến bạn không có số liệu để show lúc thuyết trình.
- **Gom chung `docker-compose.yml`:** Rất khuyến khích gom toàn bộ khối Prometheus, Grafana, Node/Windows Exporter và Agent Backend vào một file `docker-compose.yml` duy nhất. Đây là minh chứng hoàn hảo cho khả năng **"One-click deployment"** (triển khai một chạm) – một kỹ năng ăn điểm tuyệt đối trong mắt hội đồng.

### 2.3 Kịch bản Thuyết trình (Pitching & Demo Live 5-8 phút)
Hãy sử dụng đúng "từ khóa" để đánh trúng tâm lý kỹ thuật của hội đồng:
- **1 phút đầu (Vấn đề):** Dùng thuật ngữ chuyên ngành: *"Vấn đề lớn nhất của SRE/DevOps hiện nay là Alert Fatigue (Bội thực cảnh báo) và MTTR (Mean Time To Resolution - Thời gian trung bình để khắc phục) quá lâu"*.
- **2 phút tiếp (Giải pháp):** Nhấn mạnh kiến trúc **Closed-loop AIOps** (Tự động hóa vòng lặp khép kín). AI ở đây không chỉ để chat, mà tự động hóa chu trình khép vòng sự cố một cách an toàn.
- **3 phút Demo Live (Show time):** 
  - *Demo 1 (Happy Path - Dọn rác):* Mở song song màn hình Terminal và Grafana. Chạy script làm rác ổ đĩa. Cho hội đồng thấy cảnh báo tự động chuyển từ màu đỏ `Firing` sang xanh `Resolved` mà bạn không cần gõ dòng code nào.
  - *Demo 2 (Sad Path - Hacker/Injection):* Thể hiện tính bảo mật (NFR-S2). Giả lập webhook lừa AI chạy lệnh `rm -rf /`. Chỉ ngay vào Terminal để hội đồng thấy thông báo "Circuit Breaker Blocked" (Lệnh bị từ chối do ngoài Whitelist).
- **1-2 phút cuối (Tối ưu hóa - "Chốt hạ"):** Mở bảng `audit_logs` trong SQLite:
  - Chỉ vào thời gian xử lý để chứng minh SLA < 30s.
  - Chỉ vào cột Token và khẳng định: Dùng Gemini Flash-Lite có giá siêu rẻ (~$0.10/1M token) kết hợp cơ chế Fallback (dùng Rule nếu API rớt) giúp dự án đáp ứng xuất sắc tiêu chí chi phí NFR-C1.

## 3) Kiểm tra và Nghiệm thu (Definition of Done - DoD)
- [ ] File `README.md` đầy đủ hình ảnh, có sơ đồ kiến trúc và file `.env.example`.
- [ ] Khối `docker-compose` hoạt động với 1 lệnh, dữ liệu DB được lưu giữ bằng Volume.
- [ ] Kịch bản Pitching chứa thuật ngữ chuyên ngành, đi thẳng vào giải pháp và NFR.
- [ ] **💡 LỜI KHUYÊN SINH TỬ:** Đã có Video Record dự phòng! Định luật Murphy luôn xảy ra (mạng rớt, Docker lỗi). Đã tự quay lại toàn bộ màn hình 2 kịch bản Demo ở nhà. Nếu đang Live Demo bị lỗi, lập tức mở video trình chiếu để chứng minh kỹ năng Risk Management.
